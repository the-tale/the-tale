# coding: utf-8
from unittest import mock

from dext.settings import settings

from the_tale.common.utils.testcase import TestCase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import get_system_user

from the_tale.accounts.personal_messages import logic as pm_logic
from the_tale.accounts.personal_messages.tests import helpers as pm_helpers

from the_tale.game.logic import create_test_map

from the_tale.portal import signals as portal_signals
from the_tale.portal.conf import portal_settings


class DayStartedSignalTests(TestCase, pm_helpers.Mixin):

    def setUp(self):
        super(DayStartedSignalTests, self).setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account()

        pm_logic.debug_clear_service()


    def test_day_started_signal(self):
        self.assertFalse(portal_settings.SETTINGS_ACCOUNT_OF_THE_DAY_KEY in settings)

        with self.check_new_message(self.account.id, [get_system_user().id]):
            with mock.patch('the_tale.accounts.workers.accounts_manager.Worker.cmd_run_account_method') as cmd_run_account_method:
                portal_signals.day_started.send(self.__class__)

            self.assertEqual(cmd_run_account_method.call_count, 1)
            self.assertEqual(cmd_run_account_method.call_args, mock.call(account_id=self.account.id,
                                                                         method_name='prolong_premium',
                                                                         data={'days': portal_settings.PREMIUM_DAYS_FOR_HERO_OF_THE_DAY}))

            self.assertEqual(int(settings[portal_settings.SETTINGS_ACCOUNT_OF_THE_DAY_KEY]), self.account.id)


    def test_day_started_signal__only_not_premium(self):
        self.assertEqual(AccountPrototype._db_count(), 1)

        self.account.prolong_premium(days=30)
        self.account.save()

        old_premium_end_at = self.account.premium_end_at

        with self.check_no_messages(self.account.id):
            portal_signals.day_started.send(self.__class__)

        self.account.reload()
        self.assertEqual(old_premium_end_at, self.account.premium_end_at)
