# coding: utf-8

from django.test import TestCase, client
from django.contrib.auth import authenticate as django_authenticate
from django.core.urlresolvers import reverse
from django.core import mail

from dext.utils import s11n

from game.logic import create_test_map

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

def raise_exception(*argv, **kwargs): raise Exception('unknown error')

class TestResetPassword(TestCase):

    def setUp(self):
        create_test_map()
        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)

        self.client = client.Client()

    def test_reset_password(self):
        self.assertEqual(django_authenticate(username='test_user', password='111111').id, self.account.user.id)
        self.account.reset_password()
        self.assertEqual(django_authenticate(username='test_user', password='111111'), None)
        self.assertEqual(len(mail.outbox), 1)

    def test_reset_password_page_for_loggined_user(self):
        self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.get(reverse('accounts:reset-password'))
        self.assertEqual(response.status_code, 302)

    def test_reset_password_page(self):
        response = self.client.get(reverse('accounts:reset-password'))
        self.assertEqual(response.status_code, 200)

    def test_reset_password_page_for_wrong_email(self):
        response = self.client.post(reverse('accounts:reset-password'), {'email': 'wrong@test.com'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content), {'status': 'ok'})
        self.assertEqual(django_authenticate(username='test_user', password='111111').id, self.account.user.id)
        self.assertEqual(len(mail.outbox), 0)

    def test_reset_password_success(self):
        response = self.client.post(reverse('accounts:reset-password'), {'email': 'test_user@test.com'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content), {'status': 'ok'})
        self.assertEqual(django_authenticate(username='test_user', password='111111'), None)
        self.assertEqual(len(mail.outbox), 1)

    def test_reset_password_done(self):
        response = self.client.get(reverse('accounts:reset-password-done'))
        self.assertEqual(response.status_code, 200)
