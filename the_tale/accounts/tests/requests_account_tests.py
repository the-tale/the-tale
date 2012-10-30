# coding: utf-8

from django.core.urlresolvers import reverse

from common.utils.testcase import TestCase

from game.logic import create_test_map

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user
from accounts.conf import accounts_settings


class AccountRequestsTests(TestCase):

    def setUp(self):
        self.place1, self.place2, self.place3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user1', 'test_user1@test.com', '111111')
        self.account1 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user2', 'test_user2@test.com', '111111')
        self.account2 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user3', 'test_user3@test.com', '111111')
        self.account3 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user4')
        self.account4 = AccountPrototype.get_by_id(account_id)


class IndexRequestsTests(AccountRequestsTests):

    def test_index(self):
        self.check_html_ok(self.client.get(reverse('accounts:')), texts=(('pgf-account-record', 3),
                                                                         ('test_user1', 1),
                                                                         ('test_user2', 1),
                                                                         ('test_user3', 1),))

    def test_index_pagination(self):
        for i in xrange(accounts_settings.ACCOUNTS_ON_PAGE):
            register_user('test_user_%d' % i, 'test_user_%d@test.com' % i, '111111')
        self.check_html_ok(self.client.get(reverse('accounts:')), texts=(('pgf-account-record', accounts_settings.ACCOUNTS_ON_PAGE),))
        self.check_html_ok(self.client.get(reverse('accounts:')+'?page=2'), texts=(('pgf-account-record', 3),))

    def test_index_redirect_from_large_page(self):
        self.check_redirect(reverse('accounts:')+'?page=2', reverse('accounts:')+'?page=1')


class ShowRequestsTests(AccountRequestsTests):

    def test_show(self):
        self.check_html_ok(self.client.get(reverse('accounts:show', args=[self.account1.id])))

    def test_fast_account(self):
        self.check_html_ok(self.client.get(reverse('accounts:show', args=[self.account4.id])))

    def test_404(self):
        self.check_html_ok(self.client.get(reverse('accounts:show', args=['adasd'])), status_code=404)
        self.check_html_ok(self.client.get(reverse('accounts:show', args=[666])), status_code=404)
