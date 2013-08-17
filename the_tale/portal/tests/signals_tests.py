# coding: utf-8
import mock

from dext.settings import settings

from common.utils.testcase import TestCase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user, get_system_user
from accounts.personal_messages.prototypes import MessagePrototype

from game.logic import create_test_map

from portal import signals as portal_signals
from portal.conf import portal_settings


class DayStartedSignalTests(TestCase):

    def setUp(self):
        super(DayStartedSignalTests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)


    def test_day_started_signal(self):
        self.assertFalse(portal_settings.SETTINGS_ACCOUNT_OF_THE_DAY_KEY in settings)

        self.assertEqual(MessagePrototype._db_count(), 0)

        with mock.patch('accounts.workers.accounts_manager.Worker.cmd_run_account_method') as cmd_run_account_method:
            portal_signals.day_started.send(self.__class__)

        self.assertEqual(cmd_run_account_method.call_count, 1)
        self.assertEqual(cmd_run_account_method.call_args, mock.call(account_id=self.account.id,
                                                                     method_name='prolong_premium',
                                                                     data={'days': portal_settings.PREMIUM_DAYS_FOR_HERO_OF_THE_DAY}))

        self.assertEqual(int(settings[portal_settings.SETTINGS_ACCOUNT_OF_THE_DAY_KEY]), self.account.id)

        self.assertEqual(MessagePrototype._db_count(), 1)
        message = MessagePrototype._db_get_object(0)
        self.assertEqual(message.sender_id, get_system_user().id)
        self.assertEqual(message.recipient_id, self.account.id)

    def test_day_started_signal__only_not_premium(self):
        self.assertEqual(AccountPrototype._db_count(), 1)

        self.account.prolong_premium(days=30)
        self.account.save()

        old_premium_end_at = self.account.premium_end_at

        self.assertEqual(MessagePrototype._db_count(), 0)

        portal_signals.day_started.send(self.__class__)

        self.assertEqual(MessagePrototype._db_count(), 0)

        self.account.reload()
        self.assertEqual(old_premium_end_at, self.account.premium_end_at)
