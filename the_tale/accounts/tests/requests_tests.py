# coding: utf-8
from django.test import TestCase, client
from django.core.urlresolvers import reverse

from dext.utils import s11n

from accounts.logic import register_user

from game.logic import create_test_map

class TestRequests(TestCase):

    def setUp(self):
        create_test_map()
        register_user('test_user', 'test_user@test.com', '111111')
        register_user('test_user2', 'test_user2@test.com', '111111')
        self.client = client.Client()


    def login(self, email, password):
        response = self.client.post(reverse('accounts:login'), {'email': email, 'password': password})
        self.assertEqual(response.status_code, 200)

    def test_introduction_page(self):
        response = self.client.get(reverse('accounts:introduction'))
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_after_login(self):
        self.login('test_user@test.com', '111111')
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 302)

    def test_login_command(self):
        self.login('test_user@test.com', '111111')

    def test_login_after_login(self):
        self.login('test_user@test.com', '111111')

    def test_logout_command(self):
        response = self.client.post(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('application/json' in response['Content-Type'])
        self.assertEqual(s11n.from_json(response.content), {'status': 'ok'})

        response = self.client.get(reverse('accounts:logout'))
        self.assertTrue('text/html' in response['Content-Type'])
        self.assertEqual(response.status_code, 302)
