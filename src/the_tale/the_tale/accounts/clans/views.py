
import smart_imports

smart_imports.all()


class IndexFilter(utils_list_filter.ListFilter):
    ELEMENTS = [utils_list_filter.reset_element(),
                utils_list_filter.choice_element('сортировать по:', attribute='order_by', choices=relations.ORDER_BY.select('value', 'text'), default_value=relations.ORDER_BY.NAME.value)]


@dext_old_views.validator(code='clans.not_owner', message='Вы не являетесь владельцем гильдии')
def validate_ownership(resource, *args, **kwargs): return resource.clan_info.is_owner_of(resource.clan)


class ClansResource(utils_resources.Resource):

    @dext_old_views.validate_argument('clan', prototypes.ClanPrototype.get_by_id, 'clans', 'неверный идентификатор гильдии')
    def initialize(self, clan=None, *args, **kwargs):
        super(ClansResource, self).initialize(*args, **kwargs)
        self.clan = clan
        self.clan_info = logic.ClanInfo(account=self.account)

        self.can_moderate_clans = self.request.user.has_perm('clans.moderate_clan')

    @dext_old_views.validate_argument('account', accounts_prototypes.AccountPrototype.get_by_id, 'clans.account_clan', 'неверный идентификатор аккаунта')
    @dext_old_views.handler('account-clan')
    def account_clan(self, account):
        clan_info = logic.ClanInfo(account=account)
        if clan_info.clan_id is not None:
            return self.redirect(dext_urls.url('accounts:clans:show', clan_info.clan_id))
        return self.auto_error('clans.account_clan.no_clan', 'Пользователь не состоит в гильдии')

    @dext_old_views.validate_argument('page', int, 'clans', 'неверная страница')
    @dext_old_views.validate_argument('order_by', lambda o: relations.ORDER_BY(int(o)), 'clans', 'неверный параметр сортировки')
    @dext_old_views.handler('')
    def index(self, page=1, order_by=relations.ORDER_BY.NAME):

        clans_query = prototypes.ClanPrototype._model_class.objects.all()

        clans_number = clans_query.count()

        page = int(page) - 1

        url_builder = dext_urls.UrlBuilder(dext_urls.url('accounts:clans:'), arguments={'order_by': order_by.value})

        index_filter = IndexFilter(url_builder=url_builder, values={'order_by': order_by.value})

        paginator = utils_pagination.Paginator(page, clans_number, conf.settings.CLANS_ON_PAGE, url_builder)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        clans_query = clans_query.order_by(order_by.order_field)

        clans_from, clans_to = paginator.page_borders(page)

        clans = [prototypes.ClanPrototype(clan_model) for clan_model in clans_query[clans_from:clans_to]]

        memberships = [prototypes.MembershipPrototype(membership_model) for membership_model in prototypes.MembershipPrototype._db_filter(clan__in=[clan.id for clan in clans],
                                                                                                                                          role=relations.MEMBER_ROLE.LEADER)]
        accounts = {account_model.id: accounts_prototypes.AccountPrototype(model=account_model)
                    for account_model in accounts_prototypes.AccountPrototype._db_filter(id__in=[membership.account_id for membership in memberships])}
        leaders = {membership.clan_id: accounts[membership.account_id] for membership in memberships}

        return self.template('clans/index.html',
                             {'clans': clans,
                              'page_id': relations.PAGE_ID.INDEX,
                              'paginator': paginator,
                              'index_filter': index_filter,
                              'leaders': leaders})

    @dext_old_views.handler('#clan', name='show')
    def show(self):

        roles = {member.account_id: member.role for member in prototypes.MembershipPrototype.get_list_by_clan_id(self.clan.id)}
        accounts = sorted(accounts_prototypes.AccountPrototype.get_list_by_id(list(roles.keys())), key=lambda a: (roles[a.id].value, a.nick_verbose))
        heroes = {hero.account_id: hero for hero in heroes_logic.load_heroes_by_account_ids(list(roles.keys()))}

        active_accounts_number = sum((1 for account in accounts if account.is_active), 0)
        affect_game_accounts_number = sum((1 for account in accounts if account.can_affect_game), 0)

        return self.template('clans/show.html',
                             {'page_id': relations.PAGE_ID.SHOW,
                              'clan_meta_object': meta_relations.Clan.create_from_object(self.clan),
                              'roles': roles,
                              'accounts': accounts,
                              'leader': accounts[0],
                              'active_state_days': accounts_conf.settings.ACTIVE_STATE_TIMEOUT // (24 * 60 * 60),
                              'affect_game_accounts_number': affect_game_accounts_number,
                              'active_accounts_number': active_accounts_number,
                              'heroes': heroes})

    @utils_decorators.login_required
    @validate_ownership()
    @accounts_views.validate_ban_any()
    @dext_old_views.handler('#clan', 'edit')
    def edit(self):
        form = forms.ClanForm(initial={'name': self.clan.name,
                                       'abbr': self.clan.abbr,
                                       'motto': self.clan.motto,
                                       'description': self.clan.description})
        return self.template('clans/edit.html',
                             {'form': form,
                              'page_id': relations.PAGE_ID.EDIT})

    @utils_decorators.login_required
    @validate_ownership()
    @accounts_views.validate_ban_any()
    @dext_old_views.handler('#clan', 'update', method='post')
    def update(self):
        form = forms.ClanForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('clans.update.form_errors', form.errors)

        if prototypes.ClanPrototype._db_filter(name=form.c.name).exclude(id=self.clan.id).exists():
            return self.json_error('clans.update.name_exists', 'Гильдия с таким названием уже существует')

        if prototypes.ClanPrototype._db_filter(abbr=form.c.abbr).exclude(id=self.clan.id).exists():
            return self.json_error('clans.update.abbr_exists', 'Гильдия с такой аббревиатурой уже существует')

        self.clan.update(abbr=form.c.abbr,
                         name=form.c.name,
                         motto=form.c.motto,
                         description=form.c.description)

        return self.json_ok()

    @utils_decorators.login_required
    @dext_old_views.handler('#clan', 'remove', method='post')
    def remove(self):

        if not self.can_moderate_clans:

            if not self.clan_info.is_owner_of(self.clan):
                return self.json_error('clans.not_owner',
                                       'Вы не являетесь владельцем гильдии')

            if self.clan.members_number > 1:
                return self.json_error('clans.remove.not_empty_clan',
                                       'Можно удалить только «пустую» гильдию (сначала удалите всех членов кроме себя)')

        self.clan.remove()

        return self.json_ok()


@dext_old_views.validator(code='clans.membership.account_has_invite', message='Игрок уже отправил заявку на вступление или получил приглашение в вашу гильдию')
def validate_account_has_invite(resource, account, **kwargs): return prototypes.MembershipRequestPrototype.get_for(account_id=account.id, clan_id=resource.clan_info.clan_id) is None


@dext_old_views.validator(code='clans.membership.clan_has_request', message='Вы уже отправили заявку на вступление или получили приглашение в эту гильдию')
def validate_clan_has_request(resource, clan, **kwargs): return prototypes.MembershipRequestPrototype.get_for(account_id=resource.account.id, clan_id=clan.id) is None


@dext_old_views.validator(code='clans.membership.no_invite_rights', message='Вы не можете приглашать игроков в гильдию')
def validate_invite_rights(resource, *args, **kwargs): return resource.clan_info.can_invite


@dext_old_views.validator(code='clans.membership.no_remove_rights', message='Вы не можете исключать игроков в гильдию')
def validate_remove_rights(resource, *args, **kwargs): return resource.clan_info.can_remove


@dext_old_views.validator(code='clans.membership.already_in_clan', message='Вы уже состоите в гильдии')
def validate_not_in_clan(resource, *args, **kwargs): return resource.clan_info.membership is None


@dext_old_views.validator(code='clans.membership.not_in_clan', message='Вы не состоите в гильдии')
def validate_in_clan(resource, *args, **kwargs): return resource.clan_info.membership is not None


@dext_old_views.validator(code='clans.membership.other_already_in_clan', message='Игрок уже состоит в гильдии')
def validate_other_not_in_clan(resource, account, **kwargs): return logic.ClanInfo(account).membership is None


@dext_old_views.validator(code='clans.membership.request_not_from_clan', message='Запрос не от гильдии')
def validate_request_from_clan(resource, request, **kwargs): return request.type.is_FROM_CLAN


@dext_old_views.validator(code='clans.membership.request_not_from_account', message='Запрос не от аккаунта')
def validate_request_from_account(resource, request, **kwargs): return request.type.is_FROM_ACCOUNT


class MembershipResource(utils_resources.Resource):

    @utils_decorators.login_required
    @accounts_views.validate_fast_account()
    def initialize(self, *args, **kwargs):
        super(MembershipResource, self).initialize(*args, **kwargs)
        self.clan_info = logic.ClanInfo(self.account)
        self.clan = None  # Only for macros.html, TODO: remove

    @validate_invite_rights()
    @dext_old_views.handler('for-clan')
    def for_clan(self):
        self.clan = self.clan_info.clan
        requests = prototypes.MembershipRequestPrototype.get_for_clan(self.clan_info.clan_id)
        accounts = {model.id: accounts_prototypes.AccountPrototype(model) for model in accounts_prototypes.AccountPrototype._db_filter(id__in=[request.account_id for request in requests])}
        return self.template('clans/membership/for_clan.html',
                             {'requests': requests,
                              'page_id': relations.PAGE_ID.FOR_CLAN,
                              'accounts': accounts})

    @dext_old_views.handler('for-account')
    def for_account(self):
        requests = prototypes.MembershipRequestPrototype.get_for_account(self.account.id)
        accounts = {model.id: accounts_prototypes.AccountPrototype(model) for model in accounts_prototypes.AccountPrototype._db_filter(id__in=[request.account_id for request in requests] + [request.initiator_id for request in requests])}
        clans = {model.id: prototypes.ClanPrototype(model) for model in prototypes.ClanPrototype._db_filter(id__in=[request.clan_id for request in requests])}
        return self.template('clans/membership/for_account.html',
                             {'requests': requests,
                              'accounts': accounts,
                              'clans': clans,
                              'page_id': relations.PAGE_ID.FOR_ACCOUNT, })

    @dext_old_views.validate_argument('account', accounts_prototypes.AccountPrototype.get_by_id, 'clans.membership.invite', 'неверный идентификатор аккаунта')
    @validate_invite_rights()
    @validate_other_not_in_clan()
    @validate_account_has_invite()
    @accounts_views.validate_ban_any()
    @dext_old_views.handler('invite', method='get')
    def invite_dialog(self, account):
        return self.template('clans/membership/invite_dialog.html',
                             {'invited_account': account,
                              'form': forms.MembershipRequestForm()})

    @dext_old_views.validate_argument('clan', prototypes.ClanPrototype.get_by_id, 'clans.membership.request', 'неверный идентификатор гильдии')
    @validate_not_in_clan()
    @validate_clan_has_request()
    @accounts_views.validate_ban_any()
    @dext_old_views.handler('request', method='get')
    def request_dialog(self, clan):
        return self.template('clans/membership/request_dialog.html',
                             {'invited_clan': clan,
                              'form': forms.MembershipRequestForm()})

    @dext_old_views.validate_argument('account', accounts_prototypes.AccountPrototype.get_by_id, 'clans.membership.invite', 'неверный идентификатор аккаунта')
    @validate_invite_rights()
    @validate_other_not_in_clan()
    @validate_account_has_invite()
    @accounts_views.validate_ban_any()
    @dext_old_views.handler('invite', method='post')
    def invite(self, account):
        form = forms.MembershipRequestForm(self.request.POST)
        if not form.is_valid():
            return self.json_error('clans.membership.invite.form_errors', form.errors)

        request = prototypes.MembershipRequestPrototype.create(initiator=self.account,
                                                               account=account,
                                                               clan=self.clan_info.clan,
                                                               text=form.c.text,
                                                               type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_CLAN)

        request.create_invite_message(initiator=self.account)

        return self.json_ok()

    @dext_old_views.validate_argument('clan', prototypes.ClanPrototype.get_by_id, 'clans.membership.request', 'неверный идентификатор гильдии')
    @validate_not_in_clan()
    @validate_clan_has_request()
    @accounts_views.validate_ban_any()
    @dext_old_views.handler('request', method='post')
    def request_post(self, clan):
        form = forms.MembershipRequestForm(self.request.POST)
        if not form.is_valid():
            return self.json_error('clans.membership.request.form_errors', form.errors)

        request = prototypes.MembershipRequestPrototype.create(initiator=self.account,
                                                               account=self.account,
                                                               clan=clan,
                                                               text=form.c.text,
                                                               type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT)

        request.create_request_message(initiator=self.account)

        return self.json_ok()

    @django_transaction.atomic
    @dext_old_views.validate_argument('request', prototypes.MembershipRequestPrototype.get_by_id, 'clan.membership.accept_request', 'Неверный идентификатор приглашения')
    @validate_invite_rights()
    @accounts_views.validate_ban_any()
    @validate_request_from_account()
    @dext_old_views.handler('accept-request', method='post')
    def accept_request(self, request):
        accepted_account = accounts_prototypes.AccountPrototype.get_by_id(request.account_id)
        self.clan_info.clan.add_member(accepted_account)
        request.create_accept_request_message(initiator=self.account)
        request.remove()
        return self.json_ok()

    @django_transaction.atomic
    @dext_old_views.validate_argument('request', prototypes.MembershipRequestPrototype.get_by_id, 'clan.membership.accept_invite', 'Неверный идентификатор приглашения')
    @validate_not_in_clan()
    @validate_request_from_clan()
    @accounts_views.validate_ban_any()
    @dext_old_views.handler('accept-invite', method='post')
    def accept_invite(self, request):
        prototypes.ClanPrototype.get_by_id(request.clan_id).add_member(self.account)
        request.remove()
        return self.json_ok()

    @django_transaction.atomic
    @dext_old_views.validate_argument('request', prototypes.MembershipRequestPrototype.get_by_id, 'clan.membership.reject_request', 'Неверный идентификатор приглашения')
    @validate_invite_rights()
    @validate_request_from_account()
    @accounts_views.validate_ban_any()
    @dext_old_views.handler('reject-request', method='post')
    def reject_request(self, request):
        request.create_reject_request_message(initiator=self.account)
        request.remove()
        return self.json_ok()

    @django_transaction.atomic
    @dext_old_views.validate_argument('request', prototypes.MembershipRequestPrototype.get_by_id, 'clan.membership.reject_invite', 'Неверный идентификатор приглашения')
    @validate_not_in_clan()
    @validate_request_from_clan()
    @accounts_views.validate_ban_any()
    @dext_old_views.handler('reject-invite', method='post')
    def reject_invite(self, request):
        request.remove()
        return self.json_ok()

    @django_transaction.atomic
    @dext_old_views.validate_argument('account', accounts_prototypes.AccountPrototype.get_by_id, 'clan.membership.remove_from_clan', 'Неверный идентификатор пользователя')
    @validate_remove_rights()
    @accounts_views.validate_ban_any()
    @dext_old_views.handler('remove-from-clan', method='post')
    def remove_from_clan(self, account):
        other_clan_info = logic.ClanInfo(account)
        if other_clan_info.clan_id != self.clan_info.clan_id:
            return self.auto_error('clans.membership.remove_from_clan.not_in_clan', 'Игрок не состоит в вашей гильдии')

        if self.clan_info.membership.role.priority >= other_clan_info.membership.role.priority:
            return self.auto_error('clans.membership.remove_from_clan.wrong_role_priority', 'Вы не можете исключить игрока в этом звании')

        self.clan_info.clan.remove_member(account)

        self.clan_info.clan.create_remove_member_message(self.account, account)

        return self.json_ok()

    @django_transaction.atomic
    @validate_in_clan()
    @dext_old_views.handler('leave-clan', method='post')
    def leave_clan(self):
        if self.clan_info.membership.role.is_LEADER:
            return self.auto_error('clans.membership.leave_clan.leader', 'Лидер гильдии не может покинуть её. Передайте лидерство или расформируйте гильдию.')

        self.clan_info.clan.remove_member(self.account)

        return self.json_ok()
