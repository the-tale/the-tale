
import smart_imports

smart_imports.all()


class ResourceTest(testcase.TestCase):

    def setUp(self):
        super(ResourceTest, self).setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.active_end_at', datetime.datetime.now() - datetime.timedelta(seconds=1))
    def test_account_activate_unloginned(self):
        chronicle_tt_services.chronicle.cmd_debug_clear_service()

        with mock.patch('the_tale.accounts.workers.accounts_manager.Worker.cmd_run_account_method') as fake_cmd:
            self.client.get('/')

        self.assertEqual(fake_cmd.call_count, 0)

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.active_end_at', datetime.datetime.now() - datetime.timedelta(seconds=1))
    def test_account_activate_loginned(self):
        chronicle_tt_services.chronicle.cmd_debug_clear_service()

        with mock.patch('the_tale.accounts.workers.accounts_manager.Worker.cmd_run_account_method') as fake_cmd:
            self.request_login(self.account.email)
            self.client.get('/')

        self.assertEqual(fake_cmd.call_count, 1)
        self.assertEqual(fake_cmd.call_args, mock.call(account_id=self.account.id,
                                                       method_name=accounts_prototypes.AccountPrototype.update_active_state.__name__,
                                                       data={}))
