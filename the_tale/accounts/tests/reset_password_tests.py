# coding: utf-8
import mock

from django.test import client
from django.contrib.auth import authenticate as django_authenticate
from django.core.urlresolvers import reverse

from common.utils import testcase

from game.logic import create_test_map

from post_service.models import Message

from accounts.prototypes import AccountPrototype, ResetPasswordTaskPrototype
from accounts.logic import register_user
from accounts.models import ResetPasswordTask


def raise_exception(*argv, **kwargs): raise Exception('unknown error')

class ResetPasswordTaskTests(testcase.TestCase):

    def setUp(self):
        super(ResetPasswordTaskTests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)

        self.task = ResetPasswordTaskPrototype.create(self.account)

    def test_create(self):
        self.assertEqual(Message.objects.all().count(), 1)
        self.assertEqual(ResetPasswordTask.objects.all().count(), 1)

    def test_process(self):
        self.task.process()
        self.assertTrue(self.task.is_processed)
        self.assertEqual(django_authenticate(nick='test_user', password='111111'), None)


class ResetPasswordRequestsTests(testcase.TestCase):

    def setUp(self):
        super(ResetPasswordRequestsTests, self).setUp()
        create_test_map()
        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)

        self.client = client.Client()

    def test_reset_password_page_for_loggined_user(self):
        self.request_login('test_user@test.com')
        self.check_redirect(reverse('accounts:profile:reset-password'), '/')

    def test_reset_password_page(self):
        self.check_html_ok(self.client.get(reverse('accounts:profile:reset-password')))

    def test_reset_password_page_for_wrong_email(self):
        self.check_ajax_error(self.client.post(reverse('accounts:profile:reset-password'), {'email': 'wrong@test.com'}), 'accounts.profile.reset_password.wrong_email')
        self.assertEqual(django_authenticate(nick='test_user', password='111111').id, self.account.id)
        self.assertEqual(ResetPasswordTask.objects.all().count(), 0)

    def test_reset_password_success(self):
        self.check_ajax_ok(self.client.post(reverse('accounts:profile:reset-password'), {'email': 'test_user@test.com'}))
        self.assertEqual(django_authenticate(nick='test_user', password='111111').id, self.account.id)
        self.assertEqual(ResetPasswordTask.objects.all().count(), 1)

    def test_reset_password_done(self):
        self.check_html_ok(self.client.get(reverse('accounts:profile:reset-password-done')))

    def test_reset_password_processed(self):
        task = ResetPasswordTaskPrototype.create(self.account)
        self.check_html_ok(self.client.get(reverse('accounts:profile:reset-password-processed') + ('?task=%s' % task.uuid)))
        self.assertEqual(django_authenticate(nick='test_user', password='111111'), None)

    def test_reset_password_expired(self):
        task = ResetPasswordTaskPrototype.create(self.account)
        with mock.patch('accounts.conf.accounts_settings.RESET_PASSWORD_TASK_LIVE_TIME', -1):
            self.check_html_ok(self.client.get(reverse('accounts:profile:reset-password-processed') + ('?task=%s' % task.uuid)),
                               texts=['accounts.profile.reset_password_processed.time_expired'])
        self.assertEqual(django_authenticate(nick='test_user', password='111111').id, self.account.id)

    def test_reset_password_already_processed(self):
        task = ResetPasswordTaskPrototype.create(self.account)
        self.check_html_ok(self.client.get(reverse('accounts:profile:reset-password-processed') + ('?task=%s' % task.uuid)))
        self.check_html_ok(self.client.get(reverse('accounts:profile:reset-password-processed') + ('?task=%s' % task.uuid)),
                           texts=['accounts.profile.reset_password_processed.already_processed'])
