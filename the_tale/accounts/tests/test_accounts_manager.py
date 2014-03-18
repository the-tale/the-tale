# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user
from the_tale.accounts.workers.environment import workers_environment
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.logic import create_test_map



class AccountsManagerTest(testcase.TestCase):

    def setUp(self):
        super(AccountsManagerTest, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)

        workers_environment.deinitialize()
        workers_environment.initialize()

        self.worker = workers_environment.accounts_manager
        self.worker.initialize()

    def tearDown(self):
        pass

    def test_process_initialize(self):
        self.assertTrue(self.worker.initialized)

    def test_process_run_account_method__boundmethod(self):
        self.assertFalse(self.account.is_premium)
        self.worker.process_run_account_method(account_id=self.account.id,
                                               method_name=AccountPrototype.prolong_premium.__name__,
                                               data={'days': 1})
        self.account.reload()
        self.assertTrue(self.account.is_premium)
