# coding: utf-8

import mock

from dext.utils.urls import url

from common.utils.testcase import TestCase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user, login_url

from game.logic import create_test_map

from accounts.clans.prototypes import ClanPrototype
from accounts.clans.relations import ORDER_BY
from accounts.clans.views import ClansResource


class BaseTestRequests(TestCase):

    def setUp(self):
        super(BaseTestRequests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)

    def create_clan(self, owner, i):
        return ClanPrototype.create(owner=owner,
                                    abbr=u'abbr-%d' % i,
                                    name=u'name-%d' % i,
                                    motto=u'motto-%d' %i ,
                                    description=u'description-%d' % i)

class ResourceTests(BaseTestRequests):

    def setUp(self):
        super(ResourceTests, self).setUp()

    def test_can_create_clan__anonymous(self):
        resource = ClansResource(self.make_request_html(url('accounts:clans:')))
        resource.initialize()
        self.assertFalse(resource.can_create_clan)

    def test_can_create_clan__already_member(self):
        self.create_clan(self.account, 0)
        resource = ClansResource(self.make_request_html(url('accounts:clans:'), user=self.account))
        resource.initialize()
        self.assertFalse(resource.can_create_clan)

    def test_can_create_clan__is_fast(self):
        self.account.is_fast = True
        self.account.save()

        resource = ClansResource(self.make_request_html(url('accounts:clans:'), user=self.account))
        resource.initialize()
        self.assertFalse(resource.can_create_clan)

    def test_can_create_clan__can(self):
        resource = ClansResource(self.make_request_html(url('accounts:clans:'), user=self.account))
        resource.initialize()
        self.assertTrue(resource.can_create_clan)


    def test_clan_membership__anonymous(self):
        resource = ClansResource(self.make_request_html(url('accounts:clans:')))
        resource.initialize()
        self.assertEqual(resource.clan_membership, None)

    def test_clan_membership__no_membership(self):
        resource = ClansResource(self.make_request_html(url('accounts:clans:'), user=self.account))
        resource.initialize()
        self.assertEqual(resource.clan_membership, None)

    def test_clan_membership__has_membership(self):
        resource = ClansResource(self.make_request_html(url('accounts:clans:'), user=self.account))
        resource.initialize(clan=self.create_clan(self.account, 0).id)
        self.assertEqual(resource.clan_membership.account_id, self.account.id)

    def test_is_member__no_clan(self):
        resource = ClansResource(self.make_request_html(url('accounts:clans:'), user=self.account))
        resource.initialize()
        self.assertFalse(resource.is_member)

    def test_is_member__no_membership(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        account_2 = AccountPrototype.get_by_id(account_id)

        resource = ClansResource(self.make_request_html(url('accounts:clans:'), user=self.account))
        resource.initialize(clan=self.create_clan(account_2, 0).id)
        self.assertFalse(resource.is_member)

    def test_is_member__wrong_membership(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        account_2 = AccountPrototype.get_by_id(account_id)

        self.create_clan(self.account, 0)

        resource = ClansResource(self.make_request_html(url('accounts:clans:'), user=self.account))
        resource.initialize(clan=self.create_clan(account_2, 0).id)
        self.assertFalse(resource.is_member)

    def test_is_member__is_member(self):
        resource = ClansResource(self.make_request_html(url('accounts:clans:'), user=self.account))
        resource.initialize(clan=self.create_clan(self.account, 0).id)
        self.assertTrue(resource.is_member)

    @mock.patch('accounts.clans.views.ClansResource.is_member', False)
    def test_is_owner__is_member_false(self):
        resource = ClansResource(self.make_request_html(url('accounts:clans:'), user=self.account))
        resource.initialize(clan=self.create_clan(self.account, 0).id)
        self.assertFalse(resource.is_member)

    def test_is_owner__is_member_true__wrong_clan(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        account_2 = AccountPrototype.get_by_id(account_id)

        self.create_clan(self.account, 0)

        resource = ClansResource(self.make_request_html(url('accounts:clans:'), user=self.account))
        resource.initialize(clan=self.create_clan(account_2, 0).id)
        self.assertFalse(resource.is_owner)

    def test_is_owner__is_owner(self):
        resource = ClansResource(self.make_request_html(url('accounts:clans:'), user=self.account))
        resource.initialize(clan=self.create_clan(self.account, 0).id)
        self.assertTrue(resource.is_owner)




class TestIndexRequests(BaseTestRequests):

    def setUp(self):
        super(TestIndexRequests, self).setUp()

    def test_no_clans(self):
        self.check_html_ok(self.request_html(url('accounts:clans:')),
                           texts=[('pgf-no-clans-message', 1)])

    def test_create_button(self):
        with mock.patch('accounts.clans.views.ClansResource.can_create_clan', False):
            self.check_html_ok(self.request_html(url('accounts:clans:')),
                               texts=[('pgf-create-clan-button', 0)])

        with mock.patch('accounts.clans.views.ClansResource.can_create_clan', True):
            self.check_html_ok(self.request_html(url('accounts:clans:')),
                               texts=[('pgf-create-clan-button', 1)])

    @mock.patch('accounts.clans.conf.clans_settings.CLANS_ON_PAGE', 4)
    def test_clans_2_pages(self):
        for i in xrange(6):
            result, account_id, bundle_id = register_user('leader_%d' % i, 'leader_%d@test.com' % i, '111111')
            self.create_clan(AccountPrototype.get_by_id(account_id), i)

        self.check_html_ok(self.request_html(url('accounts:clans:')),
                           texts=[(u'abbr-%d' % i, 1) for i in xrange(4)] + [('pgf-no-clans-message', 0)])

        self.check_html_ok(self.request_html(url('accounts:clans:', page=2)),
                           texts=[(u'abbr-%d' % i, 1) for i in xrange(4, 6)] + [('pgf-no-clans-message', 0)])

        self.check_redirect(url('accounts:clans:', page=3), url('accounts:clans:', page=2, order_by=ORDER_BY.NAME))
