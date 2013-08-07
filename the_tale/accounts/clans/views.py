# coding: utf-8

from dext.views import handler, validate_argument, validator
from dext.utils.decorators import nested_commit_on_success
from dext.utils.urls import UrlBuilder, url

from common.utils.resources import Resource
from common.utils.decorators import login_required
from common.utils.pagination import Paginator
from common.utils import list_filter

from accounts.views import validate_fast_account
from accounts.prototypes import AccountPrototype


from accounts.clans.prototypes import ClanPrototype, MembershipPrototype, MembershipRequestPrototype
from accounts.clans.conf import clans_settings
from accounts.clans.relations import ORDER_BY, MEMBER_ROLE, PAGE_ID
from accounts.clans.forms import ClanForm, MembershipRequestForm
from accounts.clans.logic import ClanInfo


class IndexFilter(list_filter.ListFilter):
    ELEMENTS = [list_filter.reset_element(),
                list_filter.choice_element(u'сортировать по:', attribute='order_by', choices=ORDER_BY._choices(), default_value=ORDER_BY.NAME) ]



class ClansResource(Resource):

    @validate_argument('clan', ClanPrototype.get_by_id, 'clans', u'неверный идентификатор клана')
    def initialize(self, clan=None, *args, **kwargs):
        super(ClansResource, self).initialize(*args, **kwargs)
        self.clan = clan
        self.clan_info = ClanInfo(account=self.account)


    @validator(code='clans.not_owner', message=u'Вы не являетесь владельцем клана')
    def validate_ownership(self, *args, **kwargs): return self.clan_info.is_owner_of(self.clan)

    @validator(code='clans.can_not_create_clan', message=u'Вы не можете создать клан')
    def validate_creation_rights(self, *args, **kwargs): return self.clan_info.can_create_clan

    @validate_argument('page', int, 'clans', u'неверная страница')
    @validate_argument('order_by', ORDER_BY, 'clans', u'неверный параметр сортировки')
    @handler('')
    def index(self, page=1, order_by=ORDER_BY.NAME):

        clans_query = ClanPrototype._model_class.objects.all()

        clans_number = clans_query.count()

        page = int(page) - 1

        url_builder = UrlBuilder(url('accounts:clans:'), arguments={'order_by': order_by})

        index_filter = IndexFilter(url_builder=url_builder, values={'order_by': order_by})

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
    @validate_creation_rights()
    @handler('new')
    def new(self):
        return self.template('clans/new.html',
                             {'form': ClanForm(),
                              'page_id': PAGE_ID.NEW})

    @login_required
    @validate_fast_account()
    @validate_creation_rights()
    @handler('create', method='post')
    def create(self):
        form = ClanForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('clans.create.form_errors', form.errors)

        clan = ClanPrototype.create(owner=self.account,
                                    abbr=form.c.abbr,
                                    name=form.c.name,
                                    motto=form.c.motto,
                                    description=form.c.description)

        return self.json_ok(data={'next_url': url('accounts:clans:show', clan.id)})

    @handler('#clan', name='show')
    def show(self):
        return self.template('clans/show.html',
                             {'page_id': PAGE_ID.SHOW})

    @login_required
    @validate_ownership()
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
    @handler('#clan', 'update', method='post')
    def update(self):
        form = ClanForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('clans.update.form_errors', form.errors)

        self.clan.abbr = form.c.abbr
        self.clan.name = form.c.name
        self.clan.motto = form.c.motto
        self.clan.description = form.c.description

        self.clan.save()

        return self.json_ok()


    @login_required
    @validate_ownership()
    @handler('#clan', 'remove', method='post')
    def remove(self):

        self.clan.remove()

        return self.json_ok()




class MembershipResource(Resource):

    @login_required
    @validate_fast_account()
    def initialize(self, *args, **kwargs):
        super(MembershipResource, self).initialize(*args, **kwargs)
        self.clan_info = ClanInfo(self.account)
        self.clan = None # Only for macros.html, TODO: remove


    @validator(code='clans.membership.no_invite_rights', message=u'Вы не можете приглашать игроков в клан')
    def validate_invite_rights(self, *args, **kwargs): return self.clan_info.can_invite

    @validator(code='clans.membership.already_in_clan', message=u'Вы уже состоите в клане')
    def validate_not_in_clan(self, *args, **kwargs): return self.clan_info.membership is None

    @validator(code='clans.membership.other_already_in_clan', message=u'Игрок уже состоит в клане')
    def validate_other_not_in_clan(self, account, **kwargs): return ClanInfo(account).membership is None

    @validator(code='clans.membership.request_not_from_clan', message=u'Запрос не от клана')
    def validate_request_from_clan(self, request, **kwargs): return request.accepted_by_clan

    @validator(code='clans.membership.request_not_from_account', message=u'Запрос не от аккаунта')
    def validate_request_from_account(self, request, **kwargs): return request.accepted_by_account

    @validate_invite_rights()
    @handler('for-clan')
    def for_clan(self):
        requests = MembershipRequestPrototype.get_for_clan(self.clan_info.clan_id)
        accounts = {model.id: AccountPrototype(model) for model in AccountPrototype._db_filter(id__in=[request.account_id for request in requests])}
        return self.template('clans/membership/for_clan.html',
                             {'requests': requests,
                              'page_id': PAGE_ID.FOR_CLAN,
                              'accounts': accounts})

    @handler('for-account')
    def for_account(self):
        requests = MembershipRequestPrototype.get_for_account(self.account.id)
        accounts = {model.id: AccountPrototype(model) for model in AccountPrototype._db_filter(id__in=[request.account_id for request in requests])}
        return self.template('clans/membership/for_account.html',
                             {'requests': requests,
                              'accounts': accounts,
                              'page_id': PAGE_ID.FOR_ACCOUNT,})


    @validate_invite_rights()
    @validate_other_not_in_clan()
    @validate_argument('account', AccountPrototype.get_by_id, 'clans.membership.invite_dialog', u'неверный идентификатор аккаунта')
    @handler('invite', method='get')
    def invite_dialog(self, account):
        return self.template('clans/membership/invite_dialog.html',
                             {})


    @validate_not_in_clan()
    @validate_argument('clan', ClanPrototype.get_by_id, 'clans.membership.request_dialog', u'неверный идентификатор клана')
    @handler('request', method='get')
    def request_dialog(self, clan):
        return self.template('clans/membership/request_dialog.html',
                             {})


    @validate_invite_rights()
    @validate_other_not_in_clan()
    @validate_argument('account', AccountPrototype.get_by_id, 'clans.membership.invite', u'неверный идентификатор аккаунта')
    @handler('invite', method='post')
    def invite(self, account):
        form = MembershipRequestForm(self.request.POST)
        if not form.is_valid():
            return self.json_error('clans.membership.invite.form_errors', form.errors)

        MembershipRequestPrototype.create(account=account,
                                          clan=self.clan_info.clan,
                                          text=form.c.text,
                                          accepted_by_clan=True)

        return self.json_ok()


    @validate_not_in_clan()
    @validate_argument('clan', ClanPrototype.get_by_id, 'clans.membership.request', u'неверный идентификатор клана')
    @handler('request', method='get')
    def request(self, clan):
        form = MembershipRequestForm(self.request.POST)
        if not form.is_valid():
            return self.json_error('clans.membership.invite.form_errors', form.errors)

        MembershipRequestPrototype.create(account=self.account,
                                          clan=clan,
                                          text=form.c.text,
                                          accepted_by_account=True)

        return self.json_ok()

    @nested_commit_on_success
    @validate_invite_rights()
    @validate_request_from_account()
    @validate_argument('request', MembershipRequestPrototype.get_by_id, 'clan.membership.accept_request', u'Неверный идентификатор приглашения')
    @handler('accept-request', method='post')
    def accept_request(self, request):
        MembershipPrototype.create(account=AccountPrototype.get_by_id(request.account_id),
                                   clan=self.clan_info.clan,
                                   role=MEMBER_ROLE.MEMBER)

        request.remove()
        return self.json_ok()

    @nested_commit_on_success
    @validate_not_in_clan()
    @validate_request_from_clan()
    @validate_argument('request', MembershipRequestPrototype.get_by_id, 'clan.membership.accept_request', u'Неверный идентификатор приглашения')
    @handler('accept-request', method='post')
    def accept_invite(self, request):
        MembershipPrototype.create(account=AccountPrototype.get_by_id(request.account_id),
                                   clan=self.clan_info.clan,
                                   role=MEMBER_ROLE.MEMBER)

        request.remove()
        return self.json_ok()


    @nested_commit_on_success
    @validate_invite_rights()
    @validate_request_from_account()
    @validate_argument('request', MembershipRequestPrototype.get_by_id, 'clan.membership.reject_request', u'Неверный идентификатор приглашения')
    @handler('accept-request', method='post')
    def reject_request(self, request):
        request.remove()
        return self.json_ok()

    @nested_commit_on_success
    @validate_not_in_clan()
    @validate_request_from_clan()
    @validate_argument('request', MembershipRequestPrototype.get_by_id, 'clan.membership.reject_request', u'Неверный идентификатор приглашения')
    @handler('accept-request', method='post')
    def reject_invite(self, request):
        MembershipPrototype.create(account=AccountPrototype.get_by_id(request.account_id),
                                   clan=self.clan_info.clan,
                                   role=MEMBER_ROLE.MEMBER)

        request.remove()
        return self.json_ok()
