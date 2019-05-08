
import smart_imports

smart_imports.all()


def forum_subcategory_caption(clan_name):
    return 'Раздел гильдии «{}»'.format(clan_name)


def sync_clan_statistics(clan):
    clan.members_number = models.Membership.objects.filter(clan_id=clan.id).count()
    clan.active_members_number = accounts_models.Account.objects.filter(clan_id=clan.id,
                                                                        active_end_at__gt=datetime.datetime.now()).count()

    premium_members_number = 0

    for account_id in accounts_models.Account.objects.filter(clan_id=clan.id).values_list('id', flat=True):
        account = accounts_prototypes.AccountPrototype.get_by_id(account_id)

        if account.is_premium:
            premium_members_number += 1

    clan.premium_members_number = premium_members_number

    clan.might = accounts_models.Account.objects.filter(clan_id=clan.id).aggregate(might=django_models.Sum('might')).get('might', 0)

    clan.statistics_refreshed_at = datetime.datetime.now()

    models.Clan.objects.filter(id=clan.id).update(members_number=clan.members_number,
                                                  active_members_number=clan.active_members_number,
                                                  premium_members_number=clan.premium_members_number,
                                                  might=clan.might,
                                                  statistics_refreshed_at=clan.statistics_refreshed_at)


@django_transaction.atomic
def _add_member(clan, account, role):

    try:
        models.Membership.objects.create(clan_id=clan.id,
                                         account_id=account.id,
                                         role=role)
    except django_db.IntegrityError:
        raise exceptions.AddMemberFromClanError(member_id=account.id, clan_id=clan.id)

    forum_prototypes.PermissionPrototype.create(account,
                                                forum_prototypes.SubCategoryPrototype.get_by_id(clan.forum_subcategory_id))

    account.set_clan_id(clan.id)

    sync_clan_statistics(clan)

    for membership_request in requests_for_account(account.id):
        if not membership_request.type.is_FROM_CLAN:
            continue

        if membership_request.clan_id == clan.id:
            continue

        reject_invite(membership_request)

    models.MembershipRequest.objects.filter(account_id=account.id).delete()


@django_transaction.atomic
def _remove_member(clan, account):

    member_role = get_member_role(member=account, clan=clan)

    if member_role is None:
        raise exceptions.RemoveMemberFromWrongClanError(member_id=account.id, clan_id=clan.id)

    if member_role.is_MASTER:
        raise exceptions.RemoveLeaderFromClanError(member_id=account.id, clan_id=clan.id)

    models.Membership.objects.filter(clan_id=clan.id, account_id=account.id).delete()

    models.MembershipRequest.objects.filter(initiator_id=account.id).delete()

    account.set_clan_id(None)

    forum_prototypes.PermissionPrototype.get_for(account_id=account.id, subcategory_id=clan.forum_subcategory_id).remove()

    sync_clan_statistics(clan)


@django_transaction.atomic
def create_clan(owner, abbr, name, motto, description):
    forum_category = forum_prototypes.CategoryPrototype.get_by_slug(conf.settings.FORUM_CATEGORY_SLUG)

    subcategory_query = forum_prototypes.SubCategoryPrototype._db_filter(category=forum_category.id)
    subcategory_order = subcategory_query.aggregate(django_models.Max('order'))['order__max']

    if subcategory_order is None:
        subcategory_order = 0
    else:
        subcategory_order += 1

    forum_subcategory = forum_prototypes.SubCategoryPrototype.create(category=forum_category,
                                                                     caption=forum_subcategory_caption(name),
                                                                     order=subcategory_order,
                                                                     restricted=True)

    clan_model = models.Clan.objects.create(name=name,
                                            abbr=abbr,
                                            motto=motto,
                                            description=description,
                                            members_number=1,
                                            forum_subcategory=forum_subcategory._model)

    clan = load_clan(clan_model=clan_model)

    _add_member(clan=clan, account=owner, role=relations.MEMBER_ROLE.MASTER)

    tt_services.chronicle.cmd_add_event(clan=clan,
                                        event=relations.EVENT.CREATED,
                                        tags=[owner.meta_object().tag],
                                        message='Гильдия {guild} создана Хранителем {keeper}'.format(guild=clan.name,
                                                                                                     keeper=owner.nick_verbose))
    return clan


@django_transaction.atomic
def remove_clan(clan):

    models.Membership.objects.filter(clan_id=clan.id).delete()

    accounts_prototypes.AccountPrototype._db_filter(clan_id=clan.id).update(clan_id=None)

    forum_prototypes.SubCategoryPrototype.get_by_id(clan.forum_subcategory_id).delete()

    models.Clan.objects.filter(id=clan.id).delete()


def load_clan(clan_id=None, clan_model=None):

    if clan_model is None:
        try:
            clan_model = models.Clan.objects.get(id=clan_id)
        except models.Clan.DoesNotExist:
            return None

    return objects.Clan(id=clan_model.id,
                        created_at=clan_model.created_at,
                        updated_at=clan_model.updated_at,
                        members_number=clan_model.members_number,
                        active_members_number=clan_model.active_members_number,
                        premium_members_number=clan_model.premium_members_number,
                        forum_subcategory_id=clan_model.forum_subcategory_id,
                        name=clan_model.name,
                        abbr=clan_model.abbr,
                        motto=clan_model.motto,
                        description=clan_model.description,
                        might=clan_model.might,
                        statistics_refreshed_at=clan_model.statistics_refreshed_at)


def load_clans(clans_ids):
    clans = []

    for clan_model in models.Clan.objects.filter(id__in=clans_ids):
        clans.append(load_clan(clan_model=clan_model))

    return clans


@django_transaction.atomic
def save_clan(clan):
    models.Clan.objects.filter(id=clan.id).update(abbr=clan.abbr,
                                                  name=clan.name,
                                                  motto=clan.motto,
                                                  description=clan.description)

    forum_prototypes.SubCategoryPrototype._db_filter(id=clan.forum_subcategory_id).update(caption=forum_subcategory_caption(clan.name))


def get_member_role(member, clan):
    if member is None:
        return None

    if clan is None:
        return None

    try:
        return models.Membership.objects.get(account_id=member.id, clan_id=clan.id).role
    except models.Membership.DoesNotExist:
        return None


def get_membership(account_id):
    if account_id is None:
        return None

    try:
        membership_model = models.Membership.objects.get(account_id=account_id)
    except models.Membership.DoesNotExist:
        return None

    return objects.Membership(clan_id=membership_model.clan_id,
                              account_id=membership_model.account_id,
                              role=membership_model.role)


def operations_rights(initiator, clan, is_moderator):

    if clan is None:
        raise exceptions.CanNotDetermineRightsForUnknownClan()

    if initiator is None:
        raise exceptions.CanNotDetermineRightsForUnknownInitiator()

    initiator_role = get_member_role(initiator, clan)

    return objects.OperationsRights(clan_id=clan.id,
                                    initiator_role=initiator_role,
                                    is_moderator=is_moderator)


@django_transaction.atomic
def remove_member(initiator, clan, member):
    _remove_member(clan, member)

    message = 'Хранитель {initiator}s исключил(а) вас из гильдии {clan_link}.'
    message = message.format(initiator='[url="%s"]%s[/url]' % (dext_urls.full_url('https', 'accounts:show', initiator.id),
                                                               initiator.nick_verbose),
                             clan_link='[url="%s"]%s[/url]' % (dext_urls.full_url('https', 'clans:show', clan.id), clan.name))

    personal_messages_logic.send_message(sender_id=initiator.id,
                                         recipients_ids=[member.id],
                                         body=message)

    message = '{initiator} исключил(а) Хранителя {keeper} из гильдии'.format(initiator=initiator.nick_verbose,
                                                                             keeper=member.nick_verbose)

    tt_services.chronicle.cmd_add_event(clan=clan,
                                        event=relations.EVENT.MEMBER_REMOVED,
                                        tags=[initiator.meta_object().tag,
                                              member.meta_object().tag],
                                        message=message)


@django_transaction.atomic
def leave_clan(initiator, clan):
    _remove_member(clan, initiator)

    message = '{keeper} покинул(а) гильдию'.format(keeper=initiator.nick_verbose)

    tt_services.chronicle.cmd_add_event(clan=clan,
                                        event=relations.EVENT.MEMBER_LEFT,
                                        tags=[initiator.meta_object().tag],
                                        message=message)


@django_transaction.atomic
def change_role(clan, initiator, member, new_role):

    old_role = get_member_role(member, clan)

    models.Membership.objects.filter(clan_id=clan.id, account_id=member.id).update(role=new_role)

    message = 'Хранитель {initiator} изменил(а) ваше звание в гильдии {clan_link} на «{new_role}».'
    message = message.format(initiator='[url="%s"]%s[/url]' % (dext_urls.full_url('https', 'accounts:show', initiator.id),
                                                               initiator.nick_verbose),
                             clan_link='[url="%s"]%s[/url]' % (dext_urls.full_url('https', 'clans:show', clan.id),
                                                               clan.name),
                             new_role=new_role.text)

    personal_messages_logic.send_message(sender_id=initiator.id,
                                         recipients_ids=[member.id],
                                         body=message)

    message = '{initiator} изменил(а) звание Хранителя {member} с «{old_role}» на «{new_role}».'
    message = message.format(initiator=initiator.nick_verbose,
                             member=member.nick_verbose,
                             old_role=old_role.text,
                             new_role=new_role.text)

    tt_services.chronicle.cmd_add_event(clan=clan,
                                        event=relations.EVENT.ROLE_CHANGED,
                                        tags=[initiator.meta_object().tag,
                                              member.meta_object().tag],
                                        message=message)
    return dext_views.AjaxOk()


@django_transaction.atomic
def change_ownership(clan, initiator, member):
    models.Membership.objects.filter(clan_id=clan.id, role=relations.MEMBER_ROLE.MASTER).update(role=relations.MEMBER_ROLE.COMANDOR)
    models.Membership.objects.filter(clan_id=clan.id, account_id=member.id).update(role=relations.MEMBER_ROLE.MASTER)

    message = 'Магистр гильдии {initiator} передал(а) вам владение гильдией {clan_link}.'
    message = message.format(initiator='[url="%s"]%s[/url]' % (dext_urls.full_url('https', 'accounts:show', initiator.id),
                                                               initiator.nick_verbose),
                             clan_link='[url="%s"]%s[/url]' % (dext_urls.full_url('https', 'clans:show', clan.id),
                                                               clan.name))

    personal_messages_logic.send_message(sender_id=initiator.id,
                                         recipients_ids=[member.id],
                                         body=message)

    message = 'Магистр гильдии {initiator} передал(а) владение гильдией Хранителю {member}.'
    message = message.format(initiator=initiator.nick_verbose,
                             member=member.nick_verbose)

    tt_services.chronicle.cmd_add_event(clan=clan,
                                        event=relations.EVENT.OWNER_CHANGED,
                                        tags=[initiator.meta_object().tag,
                                              member.meta_object().tag],
                                        message=message)
    return dext_views.AjaxOk()



def _message_about_new_request(initiator, clan, recipient_id, text):

    message = '''
Хранитель {initiator} просит принять его в вашу гильдию:

{text}

----------
принять или отклонить предложение вы можете на этой странице: {invites_link}
'''
    message = message.format(initiator='[url="%s"]%s[/url]' % (dext_urls.full_url('https', 'accounts:show', initiator.id),
                                                               initiator.nick_verbose),
                             text=text,
                             invites_link='[url="%s"]Заявки в гильдию[/url]' % dext_urls.full_url('https', 'clans:join-requests', clan.id))

    personal_messages_logic.send_message(sender_id=initiator.id,
                                         recipients_ids=[recipient_id],
                                         body=message)


def get_recrutiers_ids(clan_id):
    roles = [role for role in relations.MEMBER_ROLE.records
             if relations.PERMISSION.TAKE_MEMBER in role.permissions]

    return models.Membership.objects.filter(clan_id=clan_id, role__in=roles).values_list('account_id', flat=True)


@django_transaction.atomic
def create_request(initiator, clan, text):
    request = models.MembershipRequest.objects.create(clan_id=clan.id,
                                                      account_id=initiator.id,
                                                      initiator_id=initiator.id,
                                                      type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT,
                                                      text=text)

    for recrutier_id in get_recrutiers_ids(clan.id):
        _message_about_new_request(initiator=initiator,
                                   clan=clan,
                                   recipient_id=recrutier_id,
                                   text=text)

    message = '{keeper} хочет вступить в гильдию'.format(keeper=initiator.nick_verbose)

    tt_services.chronicle.cmd_add_event(clan=clan,
                                        event=relations.EVENT.NEW_MEMBERSHIP_REQUEST,
                                        tags=[initiator.meta_object().tag],
                                        message=message)

    return request.id


@django_transaction.atomic
def create_invite(initiator, clan, member, text):
    request = models.MembershipRequest.objects.create(clan_id=clan.id,
                                                      account_id=member.id,
                                                      initiator_id=initiator.id,
                                                      type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_CLAN,
                                                      text=text)


    message = '''
Хранитель {initiator} предлагает вам вступить в гильдию {clan_link}:

{text}

----------
принять или отклонить предложение вы можете на этой странице: {invites_link}
'''

    message = message.format(initiator='[url="%s"]%s[/url]' % (dext_urls.full_url('https', 'accounts:show', initiator.id),
                                                               initiator.nick_verbose),
                             text=text,
                             clan_link='[url="%s"]%s[/url]' % (dext_urls.full_url('https', 'clans:show', clan.id),
                                                               clan.name),
                             invites_link='[url="%s"]Приглашения в гильдию [/url]' % dext_urls.full_url('https', 'clans:invites'))

    personal_messages_logic.send_message(sender_id=initiator.id,
                                         recipients_ids=[member.id],
                                         body=message)

    message = '{initiator} пригласил(а) Хранителя {keeper} в гильдию'.format(initiator=initiator.nick_verbose,
                                                                             keeper=member.nick_verbose)

    tt_services.chronicle.cmd_add_event(clan=clan,
                                        event=relations.EVENT.NEW_MEMBERSHIP_INVITE,
                                        tags=[initiator.meta_object().tag,
                                              member.meta_object().tag],
                                        message=message)

    return request.id


def load_request(request_id=None, request_model=None):
    if request_model is None:
        try:
            request_model = models.MembershipRequest.objects.get(id=request_id)
        except models.MembershipRequest.DoesNotExist:
            return None

    return objects.MembershipRequest(id=request_model.id,
                                     created_at=request_model.created_at,
                                     updated_at=request_model.updated_at,
                                     clan_id=request_model.clan_id,
                                     account_id=request_model.account_id,
                                     initiator_id=request_model.initiator_id,
                                     text=request_model.text,
                                     type=request_model.type)


def request_for_clan_and_account(clan_id, account_id):

    try:
        request_model = models.MembershipRequest.objects.get(account_id=account_id, clan_id=clan_id)
        return load_request(request_model=request_model)
    except models.MembershipRequest.DoesNotExist:
        return None


def requests_for_account(account_id):

    requests = []

    for request in models.MembershipRequest.objects.filter(account_id=account_id, type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_CLAN):
        requests.append(load_request(request_model=request))

    return requests


def requests_for_clan(clan_id):

    requests = []

    for request in models.MembershipRequest.objects.filter(clan_id=clan_id, type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT):
        requests.append(load_request(request_model=request))

    return requests


def requests_number_for_clan(clan_id):
    return models.MembershipRequest.objects.filter(clan_id=clan_id,
                                                   type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT).count()


@django_transaction.atomic
def reject_invite(membership_request):

    account = accounts_prototypes.AccountPrototype.get_by_id(membership_request.account_id)

    clan = load_clan(membership_request.clan_id)

    message = 'Хранитель {keeper} отказался вступить в вашу гильдию.'
    message = message.format(keeper='[url="%s"]%s[/url]' % (dext_urls.full_url('https', 'accounts:show', account.id),
                                                            account.nick_verbose))

    personal_messages_logic.send_message(sender_id=account.id,
                                         recipients_ids=[membership_request.initiator_id],
                                         body=message)

    message = '{keeper} отклонил(а) предложение вступить в гильдию'.format(keeper=account.nick_verbose)

    tt_services.chronicle.cmd_add_event(clan=clan,
                                        event=relations.EVENT.MEMBERSHIP_INVITE_REJECTED,
                                        tags=[account.meta_object().tag],
                                        message=message)

    models.MembershipRequest.objects.filter(id=membership_request.id).delete()


@django_transaction.atomic
def reject_request(initiator, membership_request):

    account = accounts_prototypes.AccountPrototype.get_by_id(membership_request.account_id)

    clan = load_clan(membership_request.clan_id)

    message = 'Хранитель {initiator} отказал вам в принятии в гильдию {clan_link}.'
    message = message.format(initiator='[url="%s"]%s[/url]' % (dext_urls.full_url('https', 'accounts:show', initiator.id),
                                                               initiator.nick_verbose),
                             clan_link='[url="%s"]%s[/url]' % (dext_urls.full_url('https', 'clans:show', clan.id),
                                                               clan.name))

    personal_messages_logic.send_message(sender_id=initiator.id,
                                         recipients_ids=[account.id],
                                         body=message)

    models.MembershipRequest.objects.filter(id=membership_request.id).delete()

    message = '{initiator} отказал(а) Хранителю {keeper} во вступлении в гильдию'.format(initiator=initiator.nick_verbose,
                                                                                         keeper=account)

    tt_services.chronicle.cmd_add_event(clan=clan,
                                        event=relations.EVENT.MEMBERSHIP_REQUEST_REJECTED,
                                        tags=[initiator.meta_object().tag,
                                              account.meta_object().tag],
                                        message=message)


@django_transaction.atomic
def accept_invite(membership_request):

    account = accounts_prototypes.AccountPrototype.get_by_id(membership_request.account_id)

    clan = load_clan(membership_request.clan_id)

    _add_member(clan=clan, account=account, role=relations.MEMBER_ROLE.RECRUIT)

    message = '{keeper} принял(а) приглашение в гильдию'.format(keeper=account.nick_verbose)

    tt_services.chronicle.cmd_add_event(clan=clan,
                                        event=relations.EVENT.MEMBERSHIP_INVITE_ACCEPTED,
                                        tags=[account.meta_object().tag],
                                        message=message)


@django_transaction.atomic
def accept_request(initiator, membership_request):
    account = accounts_prototypes.AccountPrototype.get_by_id(membership_request.account_id)

    clan = load_clan(membership_request.clan_id)

    _add_member(clan=clan, account=account, role=relations.MEMBER_ROLE.RECRUIT)

    message = 'Хранитель {initiator} принял вас в гильдию {clan_link}.'
    message = message.format(initiator='[url="%s"]%s[/url]' % (dext_urls.full_url('https', 'accounts:show', initiator.id),
                                                                initiator.nick_verbose),
                             clan_link='[url="%s"]%s[/url]' % (dext_urls.full_url('https', 'clans:show', clan.id),
                                                               clan.name))

    personal_messages_logic.send_message(sender_id=initiator.id,
                                         recipients_ids=[account.id],
                                         body=message)

    message = '{initiator} принял(а) Хранителя {keeper} в гильдию'.format(initiator=initiator.nick_verbose,
                                                                          keeper=account.nick_verbose)

    tt_services.chronicle.cmd_add_event(clan=clan,
                                        event=relations.EVENT.MEMBERSHIP_REQUEST_ACCEPTED,
                                        tags=[initiator.meta_object().tag,
                                              account.meta_object().tag],
                                        message=message)
