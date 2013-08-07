# coding: utf-8

import mock

from dext.utils.urls import url

from common.utils.testcase import TestCase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user, login_url

from game.logic import create_test_map

from accounts.clans.prototypes import ClanPrototype, MembershipPrototype, MembershipRequestPrototype
from accounts.clans.relations import ORDER_BY, MEMBER_ROLE, MEMBERSHIP_REQUEST_TYPE
from accounts.clans.tests.helpers import ClansTestsMixin


class BaseTestRequests(TestCase, ClansTestsMixin):

    def setUp(self):
        super(BaseTestRequests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)


class TestIndexRequests(BaseTestRequests):

    def setUp(self):
        super(TestIndexRequests, self).setUp()

    def test_no_clans(self):
        self.check_html_ok(self.request_html(url('accounts:clans:')),
                           texts=[('pgf-no-clans-message', 1)])

    def test_create_button(self):
        with mock.patch('accounts.clans.logic.ClanInfo.can_create_clan', False):
            self.check_html_ok(self.request_html(url('accounts:clans:')),
                               texts=[('pgf-create-clan-button', 0),
                                      ('pgf-create-clan-disabled-button', 1)])

        with mock.patch('accounts.clans.logic.ClanInfo.can_create_clan', True):
            self.check_html_ok(self.request_html(url('accounts:clans:')),
                               texts=[('pgf-create-clan-button', 1),
                                      ('pgf-create-clan-disabled-button', 0)])

    @mock.patch('accounts.clans.conf.clans_settings.CLANS_ON_PAGE', 4)
    def test_clans_2_pages(self):
        for i in xrange(6):
            result, account_id, bundle_id = register_user('leader_%d' % i, 'leader_%d@test.com' % i, '111111')
            self.create_clan(AccountPrototype.get_by_id(account_id), i)

        self.check_html_ok(self.request_html(url('accounts:clans:')),
                           texts=[(u'a-%d' % i, 1) for i in xrange(4)] + [('pgf-no-clans-message', 0)])

        self.check_html_ok(self.request_html(url('accounts:clans:', page=2)),
                           texts=[(u'a-%d' % i, 1) for i in xrange(4, 6)] + [('pgf-no-clans-message', 0)])

        self.check_redirect(url('accounts:clans:', page=3), url('accounts:clans:', page=2, order_by=ORDER_BY.NAME))


class TestNewRequests(BaseTestRequests):

    def setUp(self):
        super(TestNewRequests, self).setUp()
        self.new_url = url('accounts:clans:new')

    def test_login_required(self):
        self.check_redirect(self.new_url, login_url(self.new_url))

    def test_fast_account(self):
        self.request_login(self.account.email)
        self.account.is_fast = True
        self.account.save()
        self.check_html_ok(self.request_html(self.new_url), texts=['common.fast_account'])

    @mock.patch('accounts.clans.logic.ClanInfo.can_create_clan', False)
    def test_creation_rights(self):
        self.request_login(self.account.email)
        self.check_html_ok(self.request_html(self.new_url), texts=['clans.can_not_create_clan'])


    @mock.patch('accounts.clans.logic.ClanInfo.can_create_clan', True)
    def test_ok(self):
        self.request_login(self.account.email)
        self.check_html_ok(self.request_html(self.new_url), texts=[('clans.can_not_create_clan', 0)])


class TestCreateRequests(BaseTestRequests):

    def setUp(self):
        super(TestCreateRequests, self).setUp()
        self.create_url = url('accounts:clans:create')
        self.request_login(self.account.email)

    def create_data(self, name=None, abbr=None):
        return {'name': u'clan-1' if name is None else name,
                'abbr': u'CLN-1' if abbr is None else abbr,
                'motto': u'Clan!',
                'description': u'ARGH!'}

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(self.create_url, self.create_data()), 'common.login_required')
        self.assertEqual(ClanPrototype._db_count(), 0)

    def test_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        self.check_ajax_error(self.post_ajax_json(self.create_url, self.create_data()), 'common.fast_account')
        self.assertEqual(ClanPrototype._db_count(), 0)

    @mock.patch('accounts.clans.logic.ClanInfo.can_create_clan', False)
    def test_creation_rights(self):
        self.check_ajax_error(self.post_ajax_json(self.create_url, self.create_data()), 'clans.can_not_create_clan')
        self.assertEqual(ClanPrototype._db_count(), 0)

    @mock.patch('accounts.clans.logic.ClanInfo.can_create_clan', True)
    def test_form_errors(self):
        self.check_ajax_error(self.post_ajax_json(self.create_url, {}), 'clans.create.form_errors')
        self.assertEqual(ClanPrototype._db_count(), 0)

    @mock.patch('accounts.clans.logic.ClanInfo.can_create_clan', True)
    def test_name_exists(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        account = AccountPrototype.get_by_id(account_id)

        clan = self.create_clan(account, 0)
        self.check_ajax_error(self.post_ajax_json(self.create_url, self.create_data(name=clan.name)), 'clans.create.form_errors')
        self.assertEqual(ClanPrototype._db_count(), 1)

    @mock.patch('accounts.clans.logic.ClanInfo.can_create_clan', True)
    def test_abbr_exists(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        account = AccountPrototype.get_by_id(account_id)

        clan = self.create_clan(account, 0)
        self.check_ajax_error(self.post_ajax_json(self.create_url, self.create_data(abbr=clan.abbr)), 'clans.create.form_errors')
        self.assertEqual(ClanPrototype._db_count(), 1)

    @mock.patch('accounts.clans.logic.ClanInfo.can_create_clan', True)
    def test_ok(self):
        self.assertEqual(ClanPrototype._db_count(), 0)
        response = self.post_ajax_json(self.create_url, self.create_data())
        self.assertEqual(ClanPrototype._db_count(), 1)
        self.check_ajax_ok(response, data={'next_url': url('accounts:clans:show', ClanPrototype._db_get_object(0).id)})


class TestShowRequests(BaseTestRequests):

    def setUp(self):
        super(TestShowRequests, self).setUp()
        self.clan = self.create_clan(self.account, 0)
        self.show_url = url('accounts:clans:show', self.clan.id)

    def test_ok(self):
        self.check_html_ok(self.request_html(self.show_url), texts=[self.clan.abbr, self.clan.name, self.clan.motto, self.clan.description_html, (self.clan.description, 0)])


class TestEditRequests(BaseTestRequests):

    def setUp(self):
        super(TestEditRequests, self).setUp()
        self.clan = self.create_clan(self.account, 0)
        self.edit_url = url('accounts:clans:edit', self.clan.id)
        self.request_login(self.account.email)

    def test_login_required(self):
        self.request_logout()
        self.check_redirect(self.edit_url, login_url(self.edit_url))

    def test_ownership(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        account = AccountPrototype.get_by_id(account_id)
        clan = self.create_clan(account, 1)

        self.check_html_ok(self.request_html(url('accounts:clans:edit', clan.id)), texts=['clans.not_owner'])

    def test_ok(self):
        self.check_html_ok(self.request_html(self.edit_url), texts=[self.clan.abbr, self.clan.name, self.clan.motto, self.clan.description, (self.clan.description_html, 0)])


class TestUpdateRequests(BaseTestRequests):

    def setUp(self):
        super(TestUpdateRequests, self).setUp()
        self.clan = self.create_clan(self.account, 0)
        self.update_url = url('accounts:clans:update', self.clan.id)
        self.request_login(self.account.email)

    def update_data(self, name=None, abbr=None):
        return {'name': u'clan-1' if name is None else name,
                'abbr': u'CLN-1' if abbr is None else abbr,
                'motto': u'Clan!',
                'description': u'ARGH!'}

    def check_clan_old_data(self):
        self.clan.reload()

        self.assertEqual(u'a-0', self.clan.abbr)
        self.assertEqual(u'name-0', self.clan.name)
        self.assertEqual(u'motto-0', self.clan.motto)
        self.assertEqual(u'[b]description-0[/b]', self.clan.description)

    def check_clan_new_data(self):
        self.clan.reload()

        self.assertEqual(u'CLN-1', self.clan.abbr)
        self.assertEqual(u'clan-1', self.clan.name)
        self.assertEqual(u'Clan!', self.clan.motto)
        self.assertEqual(u'ARGH!', self.clan.description)

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(self.update_url, self.update_data()), 'common.login_required')
        self.check_clan_old_data()

    def test_ownership(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        account = AccountPrototype.get_by_id(account_id)
        clan = self.create_clan(account, 1)

        self.check_ajax_error(self.post_ajax_json(url('accounts:clans:update', clan.id)), 'clans.not_owner')
        self.check_clan_old_data()


    def test_form_errors(self):
        self.check_ajax_error(self.post_ajax_json(self.update_url, {}), 'clans.update.form_errors')
        self.check_clan_old_data()

    def test_name_exists(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        account = AccountPrototype.get_by_id(account_id)

        clan = self.create_clan(account, 1)
        self.check_ajax_error(self.post_ajax_json(self.update_url, self.update_data(name=clan.name)), 'clans.update.form_errors')

        self.check_clan_old_data()

    def test_abbr_exists(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        account = AccountPrototype.get_by_id(account_id)

        clan = self.create_clan(account, 1)
        self.check_ajax_error(self.post_ajax_json(self.update_url, self.update_data(abbr=clan.abbr)), 'clans.update.form_errors')

        self.check_clan_old_data()

    def test_ok(self):
        self.check_ajax_ok(self.post_ajax_json(self.update_url, self.update_data()))
        self.check_clan_new_data()


class TestRemoveRequests(BaseTestRequests):

    def setUp(self):
        super(TestRemoveRequests, self).setUp()
        self.clan = self.create_clan(self.account, 0)
        self.remove_url = url('accounts:clans:remove', self.clan.id)
        self.request_login(self.account.email)

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(self.remove_url), 'common.login_required')
        self.assertEqual(ClanPrototype._db_count(), 1)

    def test_ownership(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        account = AccountPrototype.get_by_id(account_id)
        clan = self.create_clan(account, 1)

        self.check_ajax_error(self.post_ajax_json(url('accounts:clans:remove', clan.id)), 'clans.not_owner')
        self.assertEqual(ClanPrototype._db_count(), 2)


    def test_ok(self):
        self.check_ajax_ok(self.post_ajax_json(self.remove_url, ))
        self.assertEqual(ClanPrototype._db_count(), 0)



class BaseMembershipRequestsTests(BaseTestRequests):

    def setUp(self):
        super(BaseMembershipRequestsTests, self).setUp()


class MembershipForClanRequestsTests(BaseMembershipRequestsTests):

    def setUp(self):
        super(MembershipForClanRequestsTests, self).setUp()
        self.for_clan_url = url('accounts:clans:membership:for-clan')
        self.clan = self.create_clan(self.account, 0)
        self.request_login(self.account.email)

    def test_login_required(self):
        self.request_logout()
        self.check_redirect(self.for_clan_url, login_url(self.for_clan_url))

    def test_has_invite_rights(self):
        MembershipPrototype._model_class.objects.all().update(role=MEMBER_ROLE.MEMBER)
        self.check_html_ok(self.request_html(self.for_clan_url), texts=['clans.membership.no_invite_rights'])

    def test_no_requests(self):
        self.check_html_ok(self.request_html(self.for_clan_url), texts=[('clans.membership.no_invite_rights', 0),
                                                                        ('pgf-no-requests-message', 1)])

    def test_success(self):

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        account_2 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')
        account_3 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_4', 'test_user_4@test.com', '111111')
        account_4 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_5', 'test_user_5@test.com', '111111')
        account_5 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_6', 'test_user_6@test.com', '111111')
        account_6 = AccountPrototype.get_by_id(account_id)

        clan_2 = self.create_clan(account_4, 1)

        MembershipRequestPrototype.create(account=account_2,
                                          clan=self.clan,
                                          text=u'invite-1',
                                          type=MEMBERSHIP_REQUEST_TYPE.FROM_CLAN)

        MembershipRequestPrototype.create(account=account_3,
                                          clan=self.clan,
                                          text=u'invite-2',
                                          type=MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT)

        MembershipRequestPrototype.create(account=account_5,
                                          clan=clan_2,
                                          text=u'invite-3',
                                          type=MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT)

        MembershipRequestPrototype.create(account=account_6,
                                          clan=clan_2,
                                          text=u'invite-4',
                                          type=MEMBERSHIP_REQUEST_TYPE.FROM_CLAN)


        self.check_html_ok(self.request_html(self.for_clan_url), texts=[('clans.membership.no_invite_rights', 0),
                                                                        ('pgf-no-requests-message', 0),
                                                                        ('invite-1', 0),
                                                                        ('invite-2', 1),
                                                                        ('invite-3', 0),
                                                                        ('invite-4', 0)])


class MembershipForAccountRequestsTests(BaseMembershipRequestsTests):

    def setUp(self):
        super(MembershipForAccountRequestsTests, self).setUp()
        self.for_account_url = url('accounts:clans:membership:for-account')
        self.request_login(self.account.email)

    def test_login_required(self):
        self.request_logout()
        self.check_redirect(self.for_account_url, login_url(self.for_account_url))

    def test_no_requests(self):
        self.check_html_ok(self.request_html(self.for_account_url), texts=[('pgf-no-requests-message', 1)])

    def test_success(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        account_2 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')
        account_3 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_4', 'test_user_4@test.com', '111111')
        account_4 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_5', 'test_user_5@test.com', '111111')
        account_5 = AccountPrototype.get_by_id(account_id)

        clan_1 = self.create_clan(account_2, 0)
        clan_2 = self.create_clan(account_4, 1)

        MembershipRequestPrototype.create(account=self.account,
                                          clan=clan_1,
                                          text=u'invite-1',
                                          type=MEMBERSHIP_REQUEST_TYPE.FROM_CLAN)

        MembershipRequestPrototype.create(account=self.account,
                                          clan=clan_1,
                                          text=u'invite-2',
                                          type=MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT)

        MembershipRequestPrototype.create(account=account_3,
                                          clan=clan_2,
                                          text=u'invite-3',
                                          type=MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT)

        MembershipRequestPrototype.create(account=account_5,
                                          clan=clan_2,
                                          text=u'invite-4',
                                          type=MEMBERSHIP_REQUEST_TYPE.FROM_CLAN)


        self.check_html_ok(self.request_html(self.for_account_url), texts=[('pgf-no-requests-message', 0),
                                                                           ('invite-1', 1),
                                                                           ('invite-2', 0),
                                                                           ('invite-3', 0),
                                                                           ('invite-4', 0) ])
