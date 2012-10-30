# coding: utf-8
from django.test import client
from django.core.urlresolvers import reverse

from dext.utils import s11n

from common.utils.testcase import TestCase

from accounts.logic import register_user, login_url

from game.logic import create_test_map

class TestRequests(TestCase):

    def setUp(self):
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account_1_id = account_id

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.account_2_id = account_id

        self.client = client.Client()


    def test_game_page_unlogined(self):
        self.check_redirect(reverse('game:'), login_url(reverse('game:')))

    def test_game_page_logined(self):
        self.request_login('test_user@test.com')
        response = self.client.get(reverse('game:'))
        self.assertEqual(response.status_code, 200)

    def test_info_unlogined(self):
        self.check_redirect(reverse('game:info'), login_url(reverse('game:info')))

    def test_info_logined(self):
        self.request_login('test_user@test.com')
        response = self.client.get(reverse('game:info'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(s11n.from_json(response.content)['data'].keys()), set(('turn', 'hero', 'abilities')))

    def test_info_other_account(self):
        self.request_login('test_user@test.com')
        response = self.client.get(reverse('game:info') + ('?account=%s' % self.account_2_id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(s11n.from_json(response.content)['data'].keys()), set(('turn', 'hero',)))

    def test_info_account_not_exists(self):
        self.request_login('test_user@test.com')
        response = self.client.get(reverse('game:info') + '?account=666')
        self.check_ajax_error(response, 'game.info.account_not_exists')

    def test_info_wrong_account_id(self):
        self.request_login('test_user@test.com')
        response = self.client.get(reverse('game:info') + '?account=sdsd')
        self.check_ajax_error(response, 'game.info.wrong_account_id')
