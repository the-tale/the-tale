# coding: utf-8
from django.test import TestCase, client
from django.core.urlresolvers import reverse

from accounts.logic import register_user

from game.logic import create_test_map

class TestRequests(TestCase):

    def setUp(self):
        create_test_map()
        register_user('test_user', 'test_user@test.com', '111111')
        self.client = client.Client()


    def test_game_page_unlogined(self):
        response = self.client.get(reverse('game:'))
        self.assertEqual(response.status_code, 200)

    def test_game_page_logined(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.get(reverse('game:'))
        self.assertEqual(response.status_code, 200)
