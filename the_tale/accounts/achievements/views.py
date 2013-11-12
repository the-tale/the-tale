# coding: utf-8

from dext.views import handler, validate_argument, validator
from dext.utils.urls import url

from the_tale.common.utils.resources import Resource
from the_tale.common.utils.decorators import login_required
from the_tale.common.utils import list_filter

from the_tale.accounts.views import validate_fast_account
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.accounts.clans.prototypes import ClanPrototype, MembershipPrototype, MembershipRequestPrototype
from the_tale.accounts.clans.conf import clans_settings
from the_tale.accounts.clans.relations import ORDER_BY, MEMBER_ROLE, PAGE_ID, MEMBERSHIP_REQUEST_TYPE
from the_tale.accounts.clans.forms import ClanForm, MembershipRequestForm

from the_tale.accounts.achievements.prototypes import AchievementPrototype, AccountAchievementsPrototype


class AchievementResource(Resource):

    @validate_argument('achievement', AchievementPrototype.get_by_id, 'accounts.achievements', u'Достижение не найдено')
    def initialize(self, achievement=None, *args, **kwargs):
        super(AchievementResource, self).initialize(*args, **kwargs)

    @handler('')
    def index(self):
        pass

    @handler('new')
    def new(self):
        pass

    @handler('create', method='post')
    def create(self):
        pass

    @handler('#achievement', 'edit')
    def edit(self):
        pass

    @handler('#achievement', 'update', method='post')
    def update(self):
        pass


class AccountAchievementsResource(Resource):

    def initialize(self, *args, **kwargs):
        super(AccountAchievementsResource, self).initialize(*args, **kwargs)

    @validate_argument('account', AccountPrototype.get_by_id, 'accounts.achievements', u'Игрок не найден')
    @handler('')
    def index(self, account=None):
        if account is None and self.account.is_authenticated():
            account = self.account

        return self.template('achievements/index.html',
                             {'master_account': account})

    @validate_argument('account', AccountPrototype.get_by_id, 'accounts.achievements', u'Игрок не найден')
    @handler('#group')
    def group(self, account):
        if account is None and self.account.is_authenticated():
            account = self.account

        return self.template('achievements/index.html',
                             {'master_account': account})
