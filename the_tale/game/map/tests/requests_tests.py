# coding: utf-8

from django.test import client
from django.core.urlresolvers import reverse

from common.utils.testcase import TestCase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.logic import create_test_map

class TestMapRequests(TestCase):

    def setUp(self):
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account = AccountPrototype.get_by_id(account_id)

        self.client = client.Client()

    def test_place_info_anonimouse(self):
        self.check_ajax_error(self.client.get(reverse('game:map:cell-info') + '?x=5&y=5', HTTP_X_REQUESTED_WITH='XMLHttpRequest'),
                              'common.login_required')

    def test_place_info_logined(self):
        self.request_login('test_user@test.com')
        self.check_html_ok(self.client.get(reverse('game:map:cell-info') + '?x=5&y=5'), texts=[('pgf-cell-debug', 0)])

    def test_place_info_logined_staff(self):
        self.request_login('test_user@test.com')
        self.account.user.is_staff = True
        self.account.user.save()
        self.check_html_ok(self.client.get(reverse('game:map:cell-info') + '?x=5&y=5'), texts=[('pgf-cell-debug', 3)])
