# coding: utf-8

from dext.views import handler, validate_argument, validator
from dext.utils.urls import UrlBuilder, url

from common.utils.resources import Resource
from common.utils.decorators import login_required, lazy_property
from common.utils.pagination import Paginator
from common.utils import list_filter

from accounts.views import validate_fast_account
from accounts.prototypes import AccountPrototype


from accounts.clans.prototypes import ClanPrototype, ClanMembershipPrototype
from accounts.clans.conf import clans_settings
from accounts.clans.relations import ORDER_BY, MEMBER_ROLE

class IndexFilter(list_filter.ListFilter):
    ELEMENTS = [list_filter.reset_element(),
                list_filter.choice_element(u'сортировать по:', attribute='order_by', choices=ORDER_BY._choices(), default_value=ORDER_BY.NAME) ]



class ClansResource(Resource):

    @validate_argument('clan', ClanPrototype.get_by_id, 'clans', u'неверный идентификатор клана')
    def initialize(self, clan=None, *args, **kwargs):
        super(ClansResource, self).initialize(*args, **kwargs)
        self.clan = clan

    @lazy_property
    def can_create_clan(self):
        return self.account.is_authenticated() and not self.account.is_fast and self.clan_membership is None

    @lazy_property
    def clan_membership(self):
        if self.account.is_authenticated():
            return ClanMembershipPrototype.get_by_account_id(self.account.id)

    @lazy_property
    def is_member(self):
        return self.clan_membership and self.clan and self.clan_membership.clan_id == self.clan.id

    @lazy_property
    def is_owner(self):
        return self.is_member and self.clan_membership.role._is_LEADER

    @validator(code='clans.not_owner', message=u'Вы не являетесь владельцем клана')
    def validate_ownership(self, *args, **kwargs): return self.is_owner

    @validator(code='clans.can_not_create_clan', message=u'Вы не можете создать клан')
    def validate_creation_rights(self, *args, **kwargs): return self.is_owner

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

        memberships = [ClanMembershipPrototype(membership_model) for membership_model in ClanMembershipPrototype._db_filter(clan__in=[clan.id for clan in clans],
                                                                                                                            role=MEMBER_ROLE.LEADER)]
        accounts = {account_model.id: AccountPrototype(model=account_model)
                    for account_model in AccountPrototype._db_filter(id__in=[membership.account_id for membership in memberships])}
        leaders = {membership.clan_id:accounts[membership.account_id] for membership in memberships}

        return self.template('clans/index.html',
                             {'clans': clans,
                              'paginator': paginator,
                              'index_filter': index_filter,
                              'leaders': leaders})


    @login_required
    @validate_fast_account()
    @validate_creation_rights()
    @handler('new')
    def new(self):
        pass

    @login_required
    @validate_fast_account()
    @validate_creation_rights()
    @handler('create', method='post')
    def create(self):
        pass

    @handler('#clan', name='show')
    def show(self):
        pass

    @login_required
    @validate_fast_account()
    @validate_ownership()
    @handler('#clan', 'edit')
    def edit(self):
        pass

    @login_required
    @validate_fast_account()
    @validate_ownership()
    @handler('#clan', 'update', method='post')
    def update(self):
        pass

    @login_required
    @validate_fast_account()
    @validate_ownership()
    @handler('#clan', 'remove', method='post')
    def remove(self):
        pass
