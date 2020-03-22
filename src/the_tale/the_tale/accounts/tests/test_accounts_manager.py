
import smart_imports

smart_imports.all()


class AccountsManagerTest(utils_testcase.TestCase):

    def setUp(self):
        super(AccountsManagerTest, self).setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

        amqp_environment.environment.deinitialize()
        amqp_environment.environment.initialize()

        self.worker = amqp_environment.environment.workers.accounts_manager
        self.worker.initialize()

    def tearDown(self):
        pass

    def test_process_initialize(self):
        self.assertTrue(self.worker.initialized)

    def test_process_run_account_method__boundmethod(self):
        self.assertFalse(self.account.is_premium)
        self.worker.process_run_account_method(account_id=self.account.id,
                                               method_name=prototypes.AccountPrototype.prolong_premium.__name__,
                                               data={'days': 1})
        self.account.reload()
        self.assertTrue(self.account.is_premium)
