# coding: utf-8

from django.core.urlresolvers import reverse

from common.utils.testcase import TestCase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.logic import create_test_map

from game.angels.conf import angels_settings


class RequestsTests(TestCase):

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


class IndexRequestsTests(RequestsTests):

    def test_index(self):
        self.check_html_ok(self.client.get(reverse('game:angels:')), texts=(('pgf-angel-record', 3),
                                                                            ('test_user1', 1),
                                                                            ('test_user2', 1),
                                                                            ('test_user3', 1),))

    def test_index_pagination(self):
        for i in xrange(angels_settings.ANGELS_ON_PAGE):
            register_user('test_user_%d' % i, 'test_user_%d@test.com' % i, '111111')
        self.check_html_ok(self.client.get(reverse('game:angels:')), texts=(('pgf-angel-record', angels_settings.ANGELS_ON_PAGE),))
        self.check_html_ok(self.client.get(reverse('game:angels:')+'?page=2'), texts=(('pgf-angel-record', 3),))

    def test_index_redirect_from_large_page(self):
        self.assertRedirects(self.client.get(reverse('game:angels:')+'?page=2'),
                             reverse('game:angels:')+'?page=1', status_code=302, target_status_code=200)


class ShowRequestsTests(RequestsTests):

    def test_show(self):
        self.check_html_ok(self.client.get(reverse('game:angels:show', args=[self.account1.angel.id])))

    def test_fast_account(self):
        self.check_html_ok(self.client.get(reverse('game:angels:show', args=[self.account4.angel.id])))

    def test_404(self):
        self.check_html_ok(self.client.get(reverse('game:angels:show', args=['adasd'])), status_code=404)
        self.check_html_ok(self.client.get(reverse('game:angels:show', args=[666])), status_code=404)
