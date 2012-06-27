# coding: utf-8
from django.test import TestCase, client
from django.core.urlresolvers import reverse

from dext.utils import s11n

from accounts.logic import register_user

from game.logic import create_test_map
from game.angels.prototypes import AngelPrototype

class TestRequests(TestCase):

    def setUp(self):
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account_1_id = account_id

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.account_2_id = account_id

        self.client = client.Client()


    def test_game_page_unlogined(self):
        response = self.client.get(reverse('game:'))
        self.assertEqual(response.status_code, 200)

    def test_game_page_logined(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.get(reverse('game:'))
        self.assertEqual(response.status_code, 200)

    def test_info_unlogined(self):
        response = self.client.get(reverse('game:info'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content)['status'], 'ok')
        self.assertEqual(set(s11n.from_json(response.content)['data'].keys()), set(('turn',)))

    def test_info_logined(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.get(reverse('game:info'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(s11n.from_json(response.content)['data'].keys()), set(('turn', 'hero',)))

    def test_info_other_angel(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.get(reverse('game:info') + ('?angel=%s' % AngelPrototype.get_by_account_id(self.account_2_id).id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(s11n.from_json(response.content)['data'].keys()), set(('turn', 'hero',)))

    def test_info_wrong_angel(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.get(reverse('game:info') + '?angel=666')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content)['status'], 'error')
