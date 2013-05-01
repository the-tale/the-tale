# coding: utf-8
import datetime

import mock

from common.utils import testcase

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

    def test_create(self):
        self.assertTrue(self.account.active_end_at > datetime.datetime.now() + datetime.timedelta(seconds=accounts_settings.ACTIVE_STATE_TIMEOUT - 60))

    @mock.patch('accounts.conf.accounts_settings.ACTIVE_STATE_REFRESH_PERIOD', 0)
    def test_update_active_state__expired(self):
        with mock.patch('game.workers.environment.workers_environment.supervisor.cmd_update_hero_with_account_data') as cmd_mark_hero_as_active:
            self.account.update_active_state()
        self.assertEqual(cmd_mark_hero_as_active.call_count, 1)

    def test_update_active_state__not_expired(self):
        with mock.patch('game.workers.environment.workers_environment.supervisor.cmd_update_hero_with_account_data') as cmd_mark_hero_as_active:
            self.account.update_active_state()
        self.assertEqual(cmd_mark_hero_as_active.call_count, 0)
