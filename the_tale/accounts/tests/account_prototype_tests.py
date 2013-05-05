# coding: utf-8
import datetime

import mock

from django.contrib.auth import authenticate as django_authenticate
from django.contrib.auth.hashers import make_password

from common.utils import testcase

from post_service.models import Message

from game.logic import create_test_map

from accounts.logic import register_user
from accounts.prototypes import AccountPrototype
from accounts.conf import accounts_settings


class AccountPrototypeTests(testcase.TestCase):

    def setUp(self):
        super(AccountPrototypeTests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('fast_user')
        self.fast_account = AccountPrototype.get_by_id(account_id)

    def test_create(self):
        self.assertTrue(self.account.active_end_at > datetime.datetime.now() + datetime.timedelta(seconds=accounts_settings.ACTIVE_STATE_TIMEOUT - 60))

    @mock.patch('accounts.conf.accounts_settings.ACTIVE_STATE_REFRESH_PERIOD', 0)
    def test_update_active_state__expired(self):
        self.assertTrue(self.account.is_update_active_state_needed)
        with mock.patch('game.workers.environment.workers_environment.supervisor.cmd_update_hero_with_account_data') as cmd_mark_hero_as_active:
            self.account.update_active_state()
        self.assertEqual(cmd_mark_hero_as_active.call_count, 1)

    def test_update_active_state__not_expired(self):
        self.assertFalse(self.account.is_update_active_state_needed)

    def test_change_credentials(self):
        self.assertTrue(AccountPrototype.get_by_id(self.fast_account.id).is_fast)

        with mock.patch('game.workers.environment.workers_environment.supervisor.cmd_update_hero_with_account_data') as fake_cmd:
            self.fast_account.change_credentials(new_email='fast_user@test.ru', new_password=make_password('222222'), new_nick='test_nick')

        self.assertEqual(django_authenticate(nick='test_nick', password='222222').id, self.fast_account.id)
        self.assertFalse(AccountPrototype.get_by_id(self.fast_account.id).is_fast)
        self.assertEqual(fake_cmd.call_count, 1)
        self.assertFalse(fake_cmd.call_args[1]['is_fast'])

    def test_change_credentials_password(self):
        self.account.change_credentials(new_password=make_password('222222'))

        self.assertEqual(Message.objects.all().count(), 0)

        self.assertEqual(self.account.email, 'test_user@test.com')
        user = django_authenticate(nick='test_user', password='222222')
        self.assertEqual(user.id, self.account.id)

    def test_change_credentials_nick(self):

        with mock.patch('game.workers.environment.workers_environment.supervisor.cmd_update_hero_with_account_data') as fake_cmd:
            self.account.change_credentials(new_nick='test_nick')

        self.assertEqual(Message.objects.all().count(), 0)
        self.assertEqual(fake_cmd.call_count, 0)
        self.assertEqual(django_authenticate(nick='test_nick', password='111111').id, self.account.id)

    def test_change_credentials_email(self):
        self.account.change_credentials(new_email='test_user@test.ru')

        self.assertEqual(Message.objects.all().count(), 0)

        self.assertEqual(self.account.email, 'test_user@test.ru')
        self.assertEqual(django_authenticate(nick='test_user', password='111111').id, self.account.id)
        self.assertEqual(django_authenticate(nick='test_user', password='111111').nick, 'test_user')

    def test_prolong_premium__for_new_premium(self):
        self.account._model.premium_end_at = datetime.datetime.now() - datetime.timedelta(days=100)

        self.account.prolong_premium(days=30)

        self.assertTrue(datetime.datetime.now() + datetime.timedelta(days=29) < self.account.premium_end_at)
        self.assertTrue(datetime.datetime.now() + datetime.timedelta(days=31) > self.account.premium_end_at)

    def test_prolong_premium__for_existed_premium(self):
        self.account._model.premium_end_at = datetime.datetime.now() + datetime.timedelta(days=100)

        self.account.prolong_premium(days=30)

        self.assertTrue(datetime.datetime.now() + datetime.timedelta(days=129) < self.account.premium_end_at)
        self.assertTrue(datetime.datetime.now() + datetime.timedelta(days=131) > self.account.premium_end_at)

    def test_is_premium(self):
        self.assertFalse(self.account.is_premium)
        self.account.prolong_premium(days=1)
        self.assertTrue(self.account.is_premium)
