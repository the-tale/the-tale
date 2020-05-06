
import smart_imports

smart_imports.all()


########################################
# processors
########################################

class ClanProcessor(utils_views.ArgumentProcessor):
    URL_NAME = 'clan'
    CONTEXT_NAME = 'current_clan'
    DEFAULT_VALUE = None
    ERROR_MESSAGE = 'Неверный идентификатор гильдии'

    def parse(self, context, raw_value):
        try:
            clan_id = int(raw_value)
        except ValueError:
            self.raise_wrong_format()

        clan = logic.load_clan(clan_id=clan_id)

        if clan is None:
            self.raise_wrong_value()

        return clan


class MembershipRequestProcessor(utils_views.ArgumentProcessor):
    GET_NAME = 'request'
    CONTEXT_NAME = 'membership_request'
    ERROR_MESSAGE = 'Неверный идентификатор запроса'

    ARG_EXPECTED_TYPE = utils_views.ProcessorArgument()

    def parse(self, context, raw_value):
        try:
            request_id = int(raw_value)
        except ValueError:
            self.raise_wrong_format()

        request = logic.load_request(request_id=request_id)

        if request is None:
            self.raise_wrong_value()

        if self.expected_type is not None and request.type != self.expected_type:
            raise utils_views.ViewError(code='clans.wrong_request_type',
                                        message='Неверный тип запроса на вступление в гильдию')

        if context.current_clan.id != request.clan_id:
            raise utils_views.ViewError(code='clans.not_your_clan_request',
                                        message='Этот запрос относится к другому клану')

        return request


class ClanRightsProcessor(utils_views.BaseViewProcessor):
    ARG_CLAN_ATTRIBUTE = utils_views.ProcessorArgument()

    def preprocess(self, context):
        rights_attribute = self.clan_attribute + '_rights'

        clan = getattr(context, self.clan_attribute, None)

        if clan is None:
            setattr(context, rights_attribute, None)
            return

        setattr(context, rights_attribute, logic.operations_rights(initiator=context.account,
                                                                   clan=clan,
                                                                   is_moderator=context.account.has_perm('clans.moderate_clan')))


class AccountClanProcessor(utils_views.BaseViewProcessor):
    ARG_ACCOUNT_ATTRIBUTE = utils_views.ProcessorArgument()
    ARG_CLAN_ATTRIBUTE = utils_views.ProcessorArgument()

    def preprocess(self, context):
        account = getattr(context, self.account_attribute, None)

        if account is None:
            setattr(context, self.clan_attribute, None)
            return

        clan = account.clan if account.is_authenticated else None

        setattr(context, self.clan_attribute, clan)


class ClanStaticOperationAccessProcessor(utils_views.AccessProcessor):
    ERROR_CODE = 'clans.no_rights'
    ERROR_MESSAGE = 'Вам запрещено проводить эту операцию'

    ARG_PERMISSION = utils_views.ProcessorArgument()
    ARG_PERMISSIONS_ATTRIBUTE = utils_views.ProcessorArgument(default='current_clan_rights')

    def validate(self, argument):
        return getattr(argument, self.permission)()

    def check(self, context):
        rights = getattr(context, self.permissions_attribute)

        if rights is None:
            return False

        return getattr(rights, self.permission)()


class ClanMemberOperationAccessProcessor(utils_views.AccessProcessor):
    ERROR_CODE = 'clans.no_rights'
    ERROR_MESSAGE = 'Вам запрещено проводить эту операцию'

    ARG_PERMISSION = utils_views.ProcessorArgument()

    def check(self, context):
        membership = logic.get_membership(context.target_account.id)

        if membership is None:
            return False

        return getattr(context.current_clan_rights, self.permission)(membership=membership)


class CanBeInvitedProcessor(utils_views.FlaggedAccessProcessor):
    ERROR_CODE = 'clans.player_does_not_accept_invites_from_clans'
    ERROR_MESSAGE = 'Игрок не хочет прнимать приглашения от гильдий'
    ARGUMENT = 'target_account'

    def validate(self, argument):
        accept_invites_from_clans = accounts_tt_services.players_properties.cmd_get_object_property(object_id=argument.id,
                                                                                                    name='accept_invites_from_clans')
        return accept_invites_from_clans


class CanReceiveRequessProcessor(utils_views.FlaggedAccessProcessor):
    ERROR_CODE = 'clans.clan_does_not_accept_requests_from_players'
    ERROR_MESSAGE = 'Гильдия не принимает запросы на вступление от игроков.'
    ARGUMENT = 'current_clan'

    def validate(self, argument):
        accept_requests_from_players = tt_services.properties.cmd_get_object_property(object_id=argument.id,
                                                                                      name='accept_requests_from_players')
        return accept_requests_from_players


class ClanIsActiveProcessor(utils_views.FlaggedAccessProcessor):
    ERROR_CODE = 'clans.removed'
    ERROR_MESSAGE = 'Гильдия распущена.'
    ARGUMENT = 'current_clan'

    def validate(self, argument):
        return argument.state.is_ACTIVE


########################################
# decorators
########################################

def change_balance_error_fabric():
    return utils_views.ViewError(code='clans.no_enought_clan_points',
                                 message='У гильдии не хватает очков действий')


points_banker = tt_services.currencies.banker(change_balance_error=change_balance_error_fabric,
                                              currency=relations.CURRENCY.ACTION_POINTS)

########################################
# resource and global processors
########################################
resource = utils_views.Resource(name='clans')
resource.add_processor(accounts_views.CurrentAccountProcessor())
resource.add_processor(utils_views.FakeResourceProcessor())
resource.add_processor(accounts_views.AccountProcessor(get_name='account', context_name='target_account', default_value=None))
resource.add_processor(ClanProcessor())
resource.add_processor(ClanRightsProcessor(clan_attribute='current_clan'))


########################################
# filters
########################################

class IndexFilter(utils_list_filter.ListFilter):
    ELEMENTS = [utils_list_filter.reset_element(),
                utils_list_filter.filter_element('поиск:', attribute='filter', default_value=None),
                utils_list_filter.choice_element('сортировать по:',
                                                 attribute='order_by',
                                                 choices=relations.ORDER_BY.select('value', 'text'),
                                                 default_value=relations.ORDER_BY.ACTIVE_MEMBERS_NUMBER_DESC.value)]


########################################
# views
########################################


@utils_views.PageNumberProcessor()
@utils_views.RelationArgumentProcessor(relation=relations.ORDER_BY,
                                       default_value=relations.ORDER_BY.ACTIVE_MEMBERS_NUMBER_DESC,
                                       error_message='неверный тип сортировки',
                                       context_name='order_by', get_name='order_by')
@utils_views.TextFilterProcessor(get_name='filter', context_name='filter', default_value=None)
@resource('')
def index(context):
    clans_query = models.Clan.objects.all()

    if context.filter:
        clans_query = clans_query.filter(django_models.Q(abbr__icontains=context.filter.strip())|
                                         django_models.Q(name__icontains=context.filter.strip()))

    clans_number = clans_query.count()

    url_builder = utils_urls.UrlBuilder(utils_urls.url('clans:'),
                                        arguments={'order_by': context.order_by.value,
                                                   'filter': context.filter})

    index_filter = IndexFilter(url_builder=url_builder, values={'order_by': context.order_by.value,
                                                                'filter': context.filter})

    paginator = utils_pagination.Paginator(context.page, clans_number, conf.settings.CLANS_ON_PAGE, url_builder)

    if paginator.wrong_page_number:
        return utils_views.Redirect(paginator.last_page_url)

    clans_query = clans_query.order_by(*context.order_by.order_field)

    clans_from, clans_to = paginator.page_borders(context.page)

    clans = [logic.load_clan(clan_model=clan_model) for clan_model in clans_query[clans_from:clans_to]]

    leaders_ids = dict(models.Membership.objects.filter(clan__in=[clan.id for clan in clans],
                                                        role=relations.MEMBER_ROLE.MASTER).values_list('clan_id', 'account_id'))

    accounts = {account_model.id: accounts_prototypes.AccountPrototype(model=account_model)
                for account_model in accounts_prototypes.AccountPrototype._db_filter(id__in=leaders_ids.values())}

    user_clan = None

    if context.account.is_authenticated and context.account.clan_id:
        user_clan = logic.load_clan(context.account.clan_id)

    return utils_views.Page('clans/index.html',
                            content={'resource': context.resource,
                                     'clans': clans,
                                     'page_id': relations.PAGE_ID.INDEX,
                                     'paginator': paginator,
                                     'index_filter': index_filter,
                                     'accounts': accounts,
                                     'leaders_ids': leaders_ids,
                                     'user_clan': user_clan,
                                     'current_clan': None})


@accounts_views.LoginRequiredProcessor()
@utils_views.PageNumberProcessor(default_value=(2 << 31))
@ClanStaticOperationAccessProcessor(permission='can_access_chronicle')
@resource('#clan', 'chronicle')
def chronicle(context):

    records_on_page = conf.settings.CHRONICLE_RECORDS_ON_CLAN_PAGE

    page, total_records, events = tt_services.chronicle.cmd_get_events(clan=context.current_clan,
                                                                       page=context.page+1,
                                                                       tags=(),
                                                                       records_on_page=records_on_page)

    page -= 1

    url_builder = utils_urls.UrlBuilder(utils_urls.url('clans:chronicle', context.current_clan.id),
                                       arguments={'page': context.page})

    if page != context.page and 'page' in context.django_request.GET:
        return utils_views.Redirect(url_builder(page=page))

    paginator = utils_pagination.Paginator(page,
                                           total_records,
                                           records_on_page,
                                           url_builder,
                                           inverse=True)

    tt_api_events_log.fill_events_wtih_meta_objects(events)

    return utils_views.Page('clans/chronicle.html',
                            content={'resource': context.resource,
                                     'events': events,
                                     'paginator': paginator,
                                     'page_id': relations.PAGE_ID.CHRONICLE,
                                     'url_builder': url_builder,
                                     'current_clan': context.current_clan})


@resource('#clan', name='show')
def show(context):

    memberships = logic.get_clan_memberships(context.current_clan.id)

    accounts = sorted(accounts_prototypes.AccountPrototype.get_list_by_id(list(memberships.keys())),
                      key=lambda a: (memberships[a.id].role.priority, a.nick_verbose))

    heroes = {hero.account_id: hero
              for hero in heroes_logic.load_heroes_by_account_ids(list(memberships.keys()))}

    total_frontier_politic_power_multiplier = sum(hero.politics_power_multiplier()
                                                  for hero in heroes.values())

    total_core_politic_power_multiplier = sum(hero.politics_power_multiplier()
                                              for hero in heroes.values()
                                              if hero.is_premium and not hero.is_banned)

    total_events, events = tt_services.chronicle.cmd_get_last_events(clan=context.current_clan,
                                                                     tags=(),
                                                                     number=conf.settings.CHRONICLE_RECORDS_ON_CLAN_PAGE)

    tt_api_events_log.fill_events_wtih_meta_objects(events)

    forum_subcategory = forum_prototypes.SubCategoryPrototype.get_by_id(context.current_clan.forum_subcategory_id)

    request_to_this_clan = None

    if context.account.is_authenticated:
        request_to_this_clan = logic.request_for_clan_and_account(clan_id=context.current_clan.id,
                                                                  account_id=context.account.id)

    requests_number_for_clan = logic.requests_number_for_clan(clan_id=context.current_clan.id)

    current_clan_properties = tt_services.properties.cmd_get_all_object_properties(context.current_clan.id)

    is_own_clan = (context.account.is_authenticated and context.account.clan_id == context.current_clan.id)

    clan_points = None
    free_quests_points = None
    experience = None

    if is_own_clan:
        clan_points = tt_services.currencies.cmd_balance(context.current_clan.id, currency=relations.CURRENCY.ACTION_POINTS)
        free_quests_points = tt_services.currencies.cmd_balance(context.current_clan.id, currency=relations.CURRENCY.FREE_QUESTS)
        experience = tt_services.currencies.cmd_balance(context.current_clan.id, currency=relations.CURRENCY.EXPERIENCE)

    emissaries = emissaries_logic.load_emissaries_for_clan(context.current_clan.id)

    emissaries_powers = politic_power_logic.get_emissaries_power([emissary.id for emissary in emissaries])

    emissaries_logic.sort_for_ui(emissaries, emissaries_powers)

    attributes = logic.load_attributes(context.current_clan.id)

    can_participate_in_pvp = emissaries_logic.can_clan_participate_in_pvp(context.current_clan.id)

    # считаем дополнительный прирост очков гильдии от мероприятий
    action_points_effects = [('гильдия', attributes.points_gain)]

    for event in emissaries_storage.events.clan_events(context.current_clan.id):
        if event.concrete_event.TYPE.is_RESERVES_SEARCH:
            action_points_effects.append((f'эмиссар {event.emissary.name}',
                                          event.concrete_event.action_points_per_step(event.concrete_event.raw_ability_power,
                                                                                      bonus=event.emissary.protectorat_event_bonus())))
    action_points_effects.sort(key=lambda effect: effect[0])
    action_points_total = sum(points for name, points in action_points_effects)

    protected_places = [place for place in places_storage.places.all() if place.attrs.clan_protector == context.current_clan.id]
    protected_places.sort(key=lambda place: place.name)

    return utils_views.Page('clans/show.html',
                            content={'resource': context.resource,
                                     'page_id': relations.PAGE_ID.SHOW,
                                     'clan_meta_object': meta_relations.Clan.create_from_object(context.current_clan),
                                     'memberships': memberships,
                                     'accounts': accounts,
                                     'leader': accounts[0] if accounts else None,
                                     'active_state_days': accounts_conf.settings.ACTIVE_STATE_TIMEOUT // (24 * 60 * 60),
                                     'total_frontier_politic_power_multiplier': total_frontier_politic_power_multiplier,
                                     'total_core_politic_power_multiplier': total_core_politic_power_multiplier,
                                     'chronicle_records': events,
                                     'total_chronicle_records': total_events,
                                     'heroes': heroes,
                                     'forum_subcategory': forum_subcategory,
                                     'request_to_this_clan': request_to_this_clan,
                                     'current_clan': context.current_clan,
                                     'current_clan_rights': context.current_clan_rights,
                                     'requests_number_for_clan': requests_number_for_clan,
                                     'current_clan_properties': current_clan_properties,
                                     'is_own_clan': is_own_clan,
                                     'clan_points': clan_points,
                                     'free_quests_points': free_quests_points,
                                     'experience': experience,
                                     'emissaries': emissaries,
                                     'attributes': attributes,
                                     'action_points_total': action_points_total,
                                     'action_points_effects': action_points_effects,
                                     'tt_clans_constants': tt_clans_constants,
                                     'emissaries_powers': emissaries_powers,
                                     'can_participate_in_pvp': can_participate_in_pvp,
                                     'protected_places': protected_places,
                                     'clans_regions': places_storage.clans_regions,
                                     'combat_personnel': logic.get_combat_personnel__by_memberships(memberships)})


@accounts_views.LoginRequiredProcessor()
@accounts_views.BanAnyProcessor()
@ClanStaticOperationAccessProcessor(permission='can_edit')
@resource('#clan', 'edit')
def edit(context):

    clan_properties = tt_services.properties.cmd_get_all_object_properties(context.current_clan.id)

    form = forms.ClanForm(initial={'name': context.current_clan.name,
                                   'abbr': context.current_clan.abbr,
                                   'motto': context.current_clan.motto,
                                   'description': context.current_clan.description,
                                   'linguistics_name': context.current_clan.linguistics_name,
                                   'accept_requests_from_players': clan_properties.accept_requests_from_players})

    return utils_views.Page('clans/edit.html',
                            content={'resource': context.resource,
                                     'form': form,
                                     'page_id': relations.PAGE_ID.EDIT,
                                     'current_clan': context.current_clan,
                                     'current_clan_rights': context.current_clan_rights})


@accounts_views.LoginRequiredProcessor()
@accounts_views.BanAnyProcessor()
@ClanStaticOperationAccessProcessor(permission='can_edit')
@utils_views.FormProcessor(form_class=forms.ClanForm)
@resource('#clan', 'update', method='POST')
def update(context):
    if models.Clan.objects.filter(name=context.form.c.name).exclude(id=context.current_clan.id).exists():
        raise utils_views.ViewError(code='clans.update.name_exists',
                                    message='Гильдия с таким названием уже существует')

    if models.Clan.objects.filter(abbr=context.form.c.abbr).exclude(id=context.current_clan.id).exists():
        raise utils_views.ViewError(code='clans.update.abbr_exists',
                                    message='Гильдия с такой аббревиатурой уже существует')

    clan = context.current_clan

    clan.abbr = context.form.c.abbr
    clan.name = context.form.c.name
    clan.motto = context.form.c.motto
    clan.description = context.form.c.description
    clan.linguistics_name = context.form.c.linguistics_name

    logic.save_clan(clan)

    tt_services.properties.cmd_set_property(context.current_clan.id,
                                            'accept_requests_from_players',
                                            context.form.c.accept_requests_from_players)

    message = 'Хранитель {keeper} изменил(а) базовые свойства гильдии {guild}'.format(guild=clan.name,
                                                                                      keeper=context.account.nick_verbose)

    tt_services.chronicle.cmd_add_event(clan=clan,
                                        event=relations.EVENT.UPDATED,
                                        tags=[context.account.meta_object().tag],
                                        message=message)

    return utils_views.AjaxOk()


@accounts_views.LoginRequiredProcessor()
@ClanStaticOperationAccessProcessor(permission='can_destroy')
@ClanIsActiveProcessor()
@resource('#clan', 'remove', method='POST')
def remove(context):

    if context.current_clan.members_number > 1:
        raise utils_views.ViewError(code='clans.remove.not_empty_clan',
                                    message='Можно удалить только «пустую» гильдию (сначала удалите всех членов кроме себя)')

    logic.remove_clan(context.current_clan)

    return utils_views.AjaxOk()


@accounts_views.LoginRequiredProcessor()
@ClanStaticOperationAccessProcessor(permission='can_take_member')
@resource('#clan', 'join-requests')
def for_clan(context):
    requests = logic.requests_for_clan(context.current_clan.id)

    accounts = {model.id: accounts_prototypes.AccountPrototype(model)
                for model in accounts_prototypes.AccountPrototype._db_filter(id__in=[request.account_id for request in requests])}

    return utils_views.Page('clans/membership/for_clan.html',
                            content={'resource': context.resource,
                                     'requests': requests,
                                     'page_id': relations.PAGE_ID.FOR_CLAN,
                                     'accounts': accounts,
                                     'current_clan': context.current_clan})


@accounts_views.LoginRequiredProcessor()
@resource('invites')
def for_account(context):
    requests = logic.requests_for_account(context.account.id)

    accounts_ids = [request.account_id for request in requests] + [request.initiator_id for request in requests]

    accounts = {model.id: accounts_prototypes.AccountPrototype(model)
                for model in accounts_prototypes.AccountPrototype._db_filter(id__in=accounts_ids)}

    clans = {clan.id: clan for clan in clans_logic.load_clans([request.clan_id for request in requests])}

    return utils_views.Page('clans/membership/for_account.html',
                            content={'resource': context.resource,
                                     'requests': requests,
                                     'accounts': accounts,
                                     'clans': clans,
                                     'page_id': relations.PAGE_ID.FOR_ACCOUNT,
                                     'current_clan': None})


def check_request_exists(account_id, clan_id, code, message):
    has_invite = models.MembershipRequest.objects.filter(account_id=account_id, clan_id=clan_id).exists()

    if has_invite:
        raise utils_views.ViewError(code=code, message=message)


def on_invite_checks(account, clan):
    if account.clan_id is not None:
        raise utils_views.ViewError(code='clans.other_already_in_clan',
                                    message='Игрок уже состоит в гильдии')

    check_request_exists(account_id=account.id,
                         clan_id=clan.id,
                         code='clans.account_has_invite',
                         message='Игрок уже отправил заявку на вступление или получил приглашение в вашу гильдию')


def on_request_checks(account, clan):
    if account.clan_id is not None:
        raise utils_views.ViewError(code='clans.already_in_clan',
                                    message='Игрок уже состоит в гильдии')

    check_request_exists(account_id=account.id,
                         clan_id=clan.id,
                         code='clans.clan_has_request',
                         message='Вы уже отправили заявку на вступление или получили приглашение в эту гильдию')


@accounts_views.LoginRequiredProcessor()
@accounts_views.BanAnyProcessor()
@CanBeInvitedProcessor()
@ClanStaticOperationAccessProcessor(permission='can_take_member')
@resource('#clan', 'invite-dialog')
def invite_dialog(context):
    on_invite_checks(context.target_account, context.current_clan)

    return utils_views.Page('clans/membership/invite_dialog.html',
                            content={'resource': context.resource,
                                     'invited_account': context.target_account,
                                     'current_clan': context.current_clan,
                                     'form': forms.MembershipRequestForm()})


@accounts_views.LoginRequiredProcessor()
@accounts_views.BanAnyProcessor()
@CanReceiveRequessProcessor()
@ClanIsActiveProcessor()
@resource('#clan', 'request-dialog')
def request_dialog(context):

    on_request_checks(context.account, context.current_clan)

    return utils_views.Page('clans/membership/request_dialog.html',
                            content={'resource': context.resource,
                                     'current_clan': context.current_clan,
                                     'form': forms.MembershipRequestForm()})


@accounts_views.LoginRequiredProcessor()
@accounts_views.BanAnyProcessor()
@ClanStaticOperationAccessProcessor(permission='can_take_member')
@CanBeInvitedProcessor()
@utils_views.FormProcessor(form_class=forms.MembershipRequestForm)
@resource('#clan', 'invite', method='POST')
def invite(context):
    on_invite_checks(context.target_account, context.current_clan)

    logic.create_invite(initiator=context.account,
                        clan=context.current_clan,
                        member=context.target_account,
                        text=context.form.c.text)

    return utils_views.AjaxOk()


@accounts_views.LoginRequiredProcessor()
@accounts_views.BanAnyProcessor()
@CanReceiveRequessProcessor()
@ClanIsActiveProcessor()
@utils_views.FormProcessor(form_class=forms.MembershipRequestForm)
@resource('#clan', 'request', method='POST')
def request(context):

    on_request_checks(context.account, clan=context.current_clan)

    logic.create_request(initiator=context.account,
                         clan=context.current_clan,
                         text=context.form.c.text)

    return utils_views.AjaxOk()


@django_transaction.atomic
@accounts_views.LoginRequiredProcessor()
@accounts_views.BanAnyProcessor()
@MembershipRequestProcessor(expected_type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT)
@ClanStaticOperationAccessProcessor(permission='can_take_member')
@resource('#clan', 'accept-request', method='POST')
def accept_request(context):

    logic.accept_request(initiator=context.account,
                         membership_request=context.membership_request)

    return utils_views.AjaxOk()


@django_transaction.atomic
@accounts_views.LoginRequiredProcessor()
@accounts_views.BanAnyProcessor()
@MembershipRequestProcessor(expected_type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_CLAN)
@resource('#clan', 'accept-invite', method='POST')
def accept_invite(context):

    if context.account.id != context.membership_request.account_id:
        raise utils_views.ViewError(code='clans.accept_request.not_your_account',
                                    message='Этот запрос относится к другому аккаунту')

    if context.account.clan_id is not None:
        raise utils_views.ViewError(code='clans.already_in_clan',
                                    message='Игрок уже состоит в гильдии')

    logic.accept_invite(membership_request=context.membership_request)

    return utils_views.AjaxOk()


@django_transaction.atomic
@accounts_views.LoginRequiredProcessor()
@accounts_views.BanAnyProcessor()
@MembershipRequestProcessor(expected_type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT)
@ClanStaticOperationAccessProcessor(permission='can_take_member')
@resource('#clan', 'reject-request', method='POST')
def reject_request(context):

    logic.reject_request(initiator=context.account,
                         membership_request=context.membership_request)

    return utils_views.AjaxOk()


@django_transaction.atomic
@accounts_views.LoginRequiredProcessor()
@accounts_views.BanAnyProcessor()
@MembershipRequestProcessor(expected_type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_CLAN)
@resource('#clan', 'reject-invite', method='POST')
def reject_invite(context):

    if context.account.id != context.membership_request.account_id:
        raise utils_views.ViewError(code='clans.accept_request.not_your_account',
                                    message='Этот запрос относится к другому аккаунту')

    logic.reject_invite(context.membership_request)

    return utils_views.AjaxOk()


@accounts_views.LoginRequiredProcessor()
@accounts_views.BanAnyProcessor()
@ClanMemberOperationAccessProcessor(permission='can_edit_member')
@resource('#clan', 'edit-member', method='GET')
def edit_member(context):

    if context.current_clan.id != context.target_account.clan_id:
        raise utils_views.ViewError(code='clans.edit.different_clans',
                                    message='Этот игрок состоит в другой гильдии')

    target_membership = logic.get_membership(context.target_account.id)

    attributes = logic.load_attributes(context.current_clan.id)

    return utils_views.Page('clans/membership/edit.html',
                            content={'resource': context.resource,
                                     'current_clan': context.current_clan,
                                     'edited_account': context.target_account,
                                     'edited_membership': target_membership,
                                     'change_role_form': forms.RoleForm(context.current_clan_rights.change_role_candidates(),
                                                                        initial={'role': target_membership.role}),
                                     'current_clan_rights': context.current_clan_rights,
                                     'attributes': attributes,
                                     'page_id': relations.PAGE_ID.EDIT_MEMBER})


@accounts_views.LoginRequiredProcessor()
@accounts_views.BanAnyProcessor()
@ClanMemberOperationAccessProcessor(permission='can_remove_member')
@resource('#clan', 'remove-member', method='POST')
def remove_from_clan(context):
    logic.remove_member(initiator=context.account,
                        clan=context.current_clan,
                        member=context.target_account)

    return utils_views.AjaxOk()


# @django_transaction.atomic
@accounts_views.LoginRequiredProcessor()
@accounts_views.BanAnyProcessor()
@ClanMemberOperationAccessProcessor(permission='can_change_role')
@resource('#clan', 'change-role', method='POST')
def change_role(context):

    form = forms.RoleForm(context.current_clan_rights.change_role_candidates(),
                          context.django_request.POST)

    if not form.is_valid():
        raise utils_views.ViewError(code='form_errors', message=form.errors)

    with django_transaction.atomic():
        logic.lock_clan_for_update(context.current_clan.id)

        old_role = logic.get_membership(context.target_account.id).role

        new_role = form.c.role

        if not logic.is_role_change_get_into_limit(context.current_clan.id, old_role, new_role):
            raise utils_views.ViewError(code='clans.fighters_maximum',
                                        message='Достигнут максимум боевого состава. Чтобы ввести Хранителя в боевой состав, необходимо сделать другого Хранителя рекрутом.')

        logic.change_role(clan=context.current_clan,
                          initiator=context.account,
                          member=context.target_account,
                          new_role=new_role)

    return utils_views.AjaxOk()


@django_transaction.atomic
@accounts_views.LoginRequiredProcessor()
@accounts_views.BanAnyProcessor()
@ClanMemberOperationAccessProcessor(permission='can_change_owner')
@resource('#clan', 'change-ownership', method='POST')
def change_ownership(context):

    if not logic.is_role_change_get_into_limit(context.current_clan.id,
                                               # старая роль нового владельца
                                               old_role=logic.get_membership(context.target_account.id).role,
                                               # будущая роль старого владельца
                                               new_role=relations.MEMBER_ROLE.COMANDOR):
        raise utils_views.ViewError(code='clans.fighters_maximum',
                                    message='Передача владения гильдией этому Хранителю приведёт к превышению максимального количества боевого состава гильдии.')

    logic.change_ownership(clan=context.current_clan,
                           initiator=context.account,
                           member=context.target_account)

    return utils_views.AjaxOk()


@django_transaction.atomic
@accounts_views.LoginRequiredProcessor()
@resource('#clan', 'leave-clan', method='POST')
def leave_clan(context):

    role = logic.get_member_role(context.account, context.current_clan)

    if role is None:
        return utils_views.AjaxOk()

    if role.is_MASTER:
        raise utils_views.ViewError(code='clans.leave_clan.leader',
                                    message='Лидер гильдии не может покинуть её. Передайте лидерство или расформируйте гильдию.')

    logic.leave_clan(initiator=context.account, clan=context.current_clan)

    return utils_views.AjaxOk()
