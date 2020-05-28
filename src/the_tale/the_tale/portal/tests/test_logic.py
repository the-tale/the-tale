
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
            logic.new_day_actions()

            border = datetime.datetime.now() + datetime.timedelta(days=conf.settings.PREMIUM_DAYS_FOR_HERO_OF_THE_DAY - 1)

            self.assertTrue(border < accounts_prototypes.AccountPrototype.get_by_id(self.account.id).premium_end_at)

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


class TypeGuardConstants(utils_testcase.TestCase):

    def test_module_constants(self):
        for module_name, module in sys.modules.items():
            if any(module_name.startswith(prefix) for prefix in ('tt_', 'the_tale')):
                if not hasattr(module, '__annotations__'):
                    continue

                for name, type_info in module.__annotations__.items():
                    typeguard.check_type(name, getattr(module, name), type_info)
