
import smart_imports

smart_imports.all()


class NewDayActionsTests(utils_testcase.TestCase,
                         personal_messages_helpers.Mixin):

    def setUp(self):
        super().setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

        personal_messages_tt_services.personal_messages.cmd_debug_clear_service()

    def test_day_started(self):
        self.assertFalse(conf.settings.SETTINGS_ACCOUNT_OF_THE_DAY_KEY in global_settings)

        with self.check_new_message(self.account.id, [accounts_logic.get_system_user().id]):
            with mock.patch('the_tale.accounts.workers.accounts_manager.Worker.cmd_run_account_method') as cmd_run_account_method:
                logic.new_day_actions()

            self.assertEqual(cmd_run_account_method.call_count, 1)
            self.assertEqual(cmd_run_account_method.call_args, mock.call(account_id=self.account.id,
                                                                         method_name='prolong_premium',
                                                                         data={'days': conf.settings.PREMIUM_DAYS_FOR_HERO_OF_THE_DAY}))

            self.assertEqual(int(global_settings[conf.settings.SETTINGS_ACCOUNT_OF_THE_DAY_KEY]), self.account.id)

    def test_day_started_signal__only_not_premium(self):
        self.assertEqual(accounts_prototypes.AccountPrototype._db_count(), 1)

        self.account.prolong_premium(days=30)
        self.account.save()

        old_premium_end_at = self.account.premium_end_at

        with self.check_no_messages(self.account.id):
            logic.new_day_actions()

        self.account.reload()
        self.assertEqual(old_premium_end_at, self.account.premium_end_at)
