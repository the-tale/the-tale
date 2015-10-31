# coding: utf-8

from django.db import transaction

from dext.views import handler, validate_argument, validator
from dext.common.utils.urls import UrlBuilder, url

from the_tale.common.utils.resources import Resource
from the_tale.common.utils.decorators import login_required
from the_tale.common.utils.pagination import Paginator
from the_tale.common.utils import list_filter

from the_tale.accounts.views import validate_fast_account, validate_ban_any
from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.conf import accounts_settings

from the_tale.game.heroes import logic as heroes_logic

from .prototypes import ClanPrototype, MembershipPrototype, MembershipRequestPrototype
from .conf import clans_settings
from .relations import ORDER_BY, MEMBER_ROLE, PAGE_ID, MEMBERSHIP_REQUEST_TYPE
from .forms import ClanForm, MembershipRequestForm
from .logic import ClanInfo
from . import meta_relations


class IndexFilter(list_filter.ListFilter):
    ELEMENTS = [list_filter.reset_element(),
                list_filter.choice_element(u'сортировать по:', attribute='order_by', choices=ORDER_BY.select('value', 'text'), default_value=ORDER_BY.NAME.value) ]



class ClansResource(Resource):

    @validate_argument('clan', ClanPrototype.get_by_id, 'clans', u'неверный идентификатор гильдии')
    def initialize(self, clan=None, *args, **kwargs):
        super(ClansResource, self).initialize(*args, **kwargs)
        self.clan = clan
        self.clan_info = ClanInfo(account=self.account)


    @validator(code='clans.not_owner', message=u'Вы не являетесь владельцем гильдии')
    def validate_ownership(self, *args, **kwargs): return self.clan_info.is_owner_of(self.clan)

    @validator(code='clans.can_not_create_clan', message=u'Вы не можете создать гильдию')
    def validate_creation_rights(self, *args, **kwargs): return self.clan_info.can_create_clan

    @validate_argument('account', AccountPrototype.get_by_id, 'clans.account_clan', u'неверный идентификатор аккаунта')
    @handler('account-clan')
    def account_clan(self, account):
        clan_info = ClanInfo(account=account)
        if clan_info.clan_id is not None:
            return self.redirect(url('accounts:clans:show', clan_info.clan_id))
        return self.auto_error('clans.account_clan.no_clan', u'Пользователь не состоит в гильдии')


    @validate_argument('page', int, 'clans', u'неверная страница')
    @validate_argument('order_by', lambda o: ORDER_BY(int(o)), 'clans', u'неверный параметр сортировки')
    @handler('')
    def index(self, page=1, order_by=ORDER_BY.NAME):

        clans_query = ClanPrototype._model_class.objects.all()

        clans_number = clans_query.count()

        page = int(page) - 1

        url_builder = UrlBuilder(url('accounts:clans:'), arguments={'order_by': order_by.value})

        index_filter = IndexFilter(url_builder=url_builder, values={'order_by': order_by.value})

        paginator = Paginator(page, clans_number, clans_settings.CLANS_ON_PAGE, url_builder)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        clans_query = clans_query.order_by(order_by.order_field)

        clans_from, clans_to = paginator.page_borders(page)

        clans = [ ClanPrototype(clan_model) for clan_model in clans_query[clans_from:clans_to]]

        memberships = [MembershipPrototype(membership_model) for membership_model in MembershipPrototype._db_filter(clan__in=[clan.id for clan in clans],
                                                                                                                    role=MEMBER_ROLE.LEADER)]
        accounts = {account_model.id: AccountPrototype(model=account_model)
                    for account_model in AccountPrototype._db_filter(id__in=[membership.account_id for membership in memberships])}
        leaders = {membership.clan_id:accounts[membership.account_id] for membership in memberships}

        return self.template('clans/index.html',
                             {'clans': clans,
                              'page_id': PAGE_ID.INDEX,
                              'paginator': paginator,
                              'index_filter': index_filter,
                              'leaders': leaders})


    @login_required
    @validate_fast_account()
    @validate_ban_any()
    @validate_creation_rights()
    @handler('new')
    def new(self):
        return self.template('clans/new.html',
                             {'form': ClanForm(),
                              'page_id': PAGE_ID.NEW})

    @login_required
    @validate_fast_account()
    @validate_ban_any()
    @validate_creation_rights()
    @handler('create', method='post')
    def create(self):
        form = ClanForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('clans.create.form_errors', form.errors)

        if ClanPrototype._db_filter(name=form.c.name).exists():
            return self.json_error('clans.create.name_exists', u'Гильдия с таким названием уже существует')

        if ClanPrototype._db_filter(abbr=form.c.abbr).exists():
            return self.json_error('clans.create.abbr_exists', u'Гильдия с такой аббревиатурой уже существует')

        clan = ClanPrototype.create(owner=self.account,
                                    abbr=form.c.abbr,
                                    name=form.c.name,
                                    motto=form.c.motto,
                                    description=form.c.description)

        return self.json_ok(data={'next_url': url('accounts:clans:show', clan.id)})

    @handler('#clan', name='show')
    def show(self):

        roles = {member.account_id:member.role for member in MembershipPrototype.get_list_by_clan_id(self.clan.id)}
        accounts = sorted(AccountPrototype.get_list_by_id(roles.keys()), key=lambda a: (roles[a.id].value, a.nick_verbose))
        heroes = {hero.account_id:hero for hero in heroes_logic.load_heroes_by_account_ids(roles.keys())}

        active_accounts_number = sum((1 for account in accounts if account.is_active), 0)
        affect_game_accounts_number = sum((1 for account in accounts if account.can_affect_game), 0)

        return self.template('clans/show.html',
                             {'page_id': PAGE_ID.SHOW,
                              'clan_meta_object': meta_relations.Clan.create_from_object(self.clan),
                              'roles': roles,
                              'accounts': accounts,
                              'leader': accounts[0],
                              'active_state_days': accounts_settings.ACTIVE_STATE_TIMEOUT / (24*60*60),
                              'affect_game_accounts_number': affect_game_accounts_number,
                              'active_accounts_number': active_accounts_number,
                              'heroes': heroes})

    @login_required
    @validate_ownership()
    @validate_ban_any()
    @handler('#clan', 'edit')
    def edit(self):
        form = ClanForm(initial={'name': self.clan.name,
                                 'abbr': self.clan.abbr,
                                 'motto': self.clan.motto,
                                 'description': self.clan.description})
        return self.template('clans/edit.html',
                             {'form': form,
                              'page_id': PAGE_ID.EDIT})

    @login_required
    @validate_ownership()
    @validate_ban_any()
    @handler('#clan', 'update', method='post')
    def update(self):
        form = ClanForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('clans.update.form_errors', form.errors)

        if ClanPrototype._db_filter(name=form.c.name).exclude(id=self.clan.id).exists():
            return self.json_error('clans.update.name_exists', u'Гильдия с таким названием уже существует')

        if ClanPrototype._db_filter(abbr=form.c.abbr).exclude(id=self.clan.id).exists():
            return self.json_error('clans.update.abbr_exists', u'Гильдия с такой аббревиатурой уже существует')


        self.clan.update(abbr=form.c.abbr,
                         name=form.c.name,
                         motto=form.c.motto,
                         description=form.c.description)

        return self.json_ok()


    @login_required
    @validate_ownership()
    @handler('#clan', 'remove', method='post')
    def remove(self):

        if self.clan.members_number > 1:
            return self.json_error('clans.remove.not_empty_clan', u'Можно удалить только «пустую» гильдию (сначала удалите всех членов кроме себя)')

        self.clan.remove()

        return self.json_ok()




class MembershipResource(Resource):

    @login_required
    @validate_fast_account()
    def initialize(self, *args, **kwargs):
        super(MembershipResource, self).initialize(*args, **kwargs)
        self.clan_info = ClanInfo(self.account)
        self.clan = None # Only for macros.html, TODO: remove


    @validator(code='clans.membership.no_invite_rights', message=u'Вы не можете приглашать игроков в гильдию')
    def validate_invite_rights(self, *args, **kwargs): return self.clan_info.can_invite

    @validator(code='clans.membership.no_remove_rights', message=u'Вы не можете исключать игроков в гильдию')
    def validate_remove_rights(self, *args, **kwargs): return self.clan_info.can_remove

    @validator(code='clans.membership.already_in_clan', message=u'Вы уже состоите в гильдии')
    def validate_not_in_clan(self, *args, **kwargs): return self.clan_info.membership is None

    @validator(code='clans.membership.not_in_clan', message=u'Вы не состоите в гильдии')
    def validate_in_clan(self, *args, **kwargs): return self.clan_info.membership is not None

    @validator(code='clans.membership.other_already_in_clan', message=u'Игрок уже состоит в гильдии')
    def validate_other_not_in_clan(self, account, **kwargs): return ClanInfo(account).membership is None

    @validator(code='clans.membership.request_not_from_clan', message=u'Запрос не от гильдии')
    def validate_request_from_clan(self, request, **kwargs): return request.type.is_FROM_CLAN

    @validator(code='clans.membership.request_not_from_account', message=u'Запрос не от аккаунта')
    def validate_request_from_account(self, request, **kwargs): return request.type.is_FROM_ACCOUNT

    @validator(code='clans.membership.account_has_invite', message=u'Игрок уже отправил заявку на вступление или получил приглашение в вашу гильдию')
    def validate_account_has_invite(self, account, **kwargs): return MembershipRequestPrototype.get_for(account_id=account.id, clan_id=self.clan_info.clan_id) is None

    @validator(code='clans.membership.clan_has_request', message=u'Вы уже отправили заявку на вступление или получили приглашение в эту гильдию')
    def validate_clan_has_request(self, clan, **kwargs): return MembershipRequestPrototype.get_for(account_id=self.account.id, clan_id=clan.id) is None

    @validate_invite_rights()
    @handler('for-clan')
    def for_clan(self):
        self.clan = self.clan_info.clan
        requests = MembershipRequestPrototype.get_for_clan(self.clan_info.clan_id)
        accounts = {model.id: AccountPrototype(model) for model in AccountPrototype._db_filter(id__in=[request.account_id for request in requests])}
        return self.template('clans/membership/for_clan.html',
                             {'requests': requests,
                              'page_id': PAGE_ID.FOR_CLAN,
                              'accounts': accounts})

    @handler('for-account')
    def for_account(self):
        requests = MembershipRequestPrototype.get_for_account(self.account.id)
        accounts = {model.id: AccountPrototype(model) for model in AccountPrototype._db_filter(id__in=[request.account_id for request in requests] + [request.initiator_id for request in requests])}
        clans = {model.id: ClanPrototype(model) for model in ClanPrototype._db_filter(id__in=[request.clan_id for request in requests])}
        return self.template('clans/membership/for_account.html',
                             {'requests': requests,
                              'accounts': accounts,
                              'clans': clans,
                              'page_id': PAGE_ID.FOR_ACCOUNT,})


    @validate_argument('account', AccountPrototype.get_by_id, 'clans.membership.invite', u'неверный идентификатор аккаунта')
    @validate_invite_rights()
    @validate_other_not_in_clan()
    @validate_account_has_invite()
    @validate_ban_any()
    @handler('invite', method='get')
    def invite_dialog(self, account):
        return self.template('clans/membership/invite_dialog.html',
                             {'invited_account': account,
                              'form': MembershipRequestForm()})


    @validate_argument('clan', ClanPrototype.get_by_id, 'clans.membership.request', u'неверный идентификатор гильдии')
    @validate_not_in_clan()
    @validate_clan_has_request()
    @validate_ban_any()
    @handler('request', method='get')
    def request_dialog(self, clan):
        return self.template('clans/membership/request_dialog.html',
                             {'invited_clan': clan,
                              'form': MembershipRequestForm()})


    @validate_argument('account', AccountPrototype.get_by_id, 'clans.membership.invite', u'неверный идентификатор аккаунта')
    @validate_invite_rights()
    @validate_other_not_in_clan()
    @validate_account_has_invite()
    @validate_ban_any()
    @handler('invite', method='post')
    def invite(self, account):
        form = MembershipRequestForm(self.request.POST)
        if not form.is_valid():
            return self.json_error('clans.membership.invite.form_errors', form.errors)

        request = MembershipRequestPrototype.create(initiator=self.account,
                                                    account=account,
                                                    clan=self.clan_info.clan,
                                                    text=form.c.text,
                                                    type=MEMBERSHIP_REQUEST_TYPE.FROM_CLAN)

        request.create_invite_message(initiator=self.account)

        return self.json_ok()


    @validate_argument('clan', ClanPrototype.get_by_id, 'clans.membership.request', u'неверный идентификатор гильдии')
    @validate_not_in_clan()
    @validate_clan_has_request()
    @validate_ban_any()
    @handler('request', method='post')
    def request_post(self, clan):
        form = MembershipRequestForm(self.request.POST)
        if not form.is_valid():
            return self.json_error('clans.membership.request.form_errors', form.errors)

        request = MembershipRequestPrototype.create(initiator=self.account,
                                                    account=self.account,
                                                    clan=clan,
                                                    text=form.c.text,
                                                    type=MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT)

        request.create_request_message(initiator=self.account)

        return self.json_ok()

    @transaction.atomic
    @validate_argument('request', MembershipRequestPrototype.get_by_id, 'clan.membership.accept_request', u'Неверный идентификатор приглашения')
    @validate_invite_rights()
    @validate_ban_any()
    @validate_request_from_account()
    @handler('accept-request', method='post')
    def accept_request(self, request):
        accepted_account = AccountPrototype.get_by_id(request.account_id)
        self.clan_info.clan.add_member(accepted_account)
        request.create_accept_request_message(initiator=self.account)
        request.remove()
        return self.json_ok()

    @transaction.atomic
    @validate_argument('request', MembershipRequestPrototype.get_by_id, 'clan.membership.accept_invite', u'Неверный идентификатор приглашения')
    @validate_not_in_clan()
    @validate_request_from_clan()
    @validate_ban_any()
    @handler('accept-invite', method='post')
    def accept_invite(self, request):
        ClanPrototype.get_by_id(request.clan_id).add_member(self.account)
        request.remove()
        return self.json_ok()


    @transaction.atomic
    @validate_argument('request', MembershipRequestPrototype.get_by_id, 'clan.membership.reject_request', u'Неверный идентификатор приглашения')
    @validate_invite_rights()
    @validate_request_from_account()
    @validate_ban_any()
    @handler('reject-request', method='post')
    def reject_request(self, request):
        request.create_reject_request_message(initiator=self.account)
        request.remove()
        return self.json_ok()

    @transaction.atomic
    @validate_argument('request', MembershipRequestPrototype.get_by_id, 'clan.membership.reject_invite', u'Неверный идентификатор приглашения')
    @validate_not_in_clan()
    @validate_request_from_clan()
    @validate_ban_any()
    @handler('reject-invite', method='post')
    def reject_invite(self, request):
        request.remove()
        return self.json_ok()

    @transaction.atomic
    @validate_argument('account', AccountPrototype.get_by_id, 'clan.membership.remove_from_clan', u'Неверный идентификатор пользователя')
    @validate_remove_rights()
    @validate_ban_any()
    @handler('remove-from-clan', method='post')
    def remove_from_clan(self, account):
        other_clan_info = ClanInfo(account)
        if other_clan_info.clan_id != self.clan_info.clan_id:
            return self.auto_error('clans.membership.remove_from_clan.not_in_clan', u'Игрок не состоит в вашей гильдии')

        if self.clan_info.membership.role.priority >= other_clan_info.membership.role.priority:
            return self.auto_error('clans.membership.remove_from_clan.wrong_role_priority', u'Вы не можете исключить игрока в этом звании')

        self.clan_info.clan.remove_member(account)

        self.clan_info.clan.create_remove_member_message(self.account, account)

        return self.json_ok()


    @transaction.atomic
    @validate_in_clan()
    @handler('leave-clan', method='post')
    def leave_clan(self):
        if self.clan_info.membership.role.is_LEADER:
            return self.auto_error('clans.membership.leave_clan.leader', u'Лидер гильдии не может покинуть её. Передайте лидерство или расформируйте гильдию.')

        self.clan_info.clan.remove_member(self.account)

        return self.json_ok()
