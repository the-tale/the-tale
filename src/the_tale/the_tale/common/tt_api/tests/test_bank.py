
import smart_imports

smart_imports.all()


bank_client = bank.Client(entry_point=game_conf.settings.TT_ENERGY_ENTRY_POINT,
                          transaction_lifetime=60)


class TTBankAPiTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        bank_client.cmd_debug_clear_service()

    def test_change_balance__no_autocommit_in_async_request(self):
        with self.assertRaises(exceptions.AutocommitRequiredForAsyncTransaction):
            bank_client.cmd_change_balance(account_id=666, type='test', energy=1, async=True, autocommit=False)

    def test_change_balance__async(self):
        with self.check_delta(lambda: bank_client.cmd_balance(account_id=666), 1):
            status, transaction_id = bank_client.cmd_change_balance(account_id=666, type='test', energy=1, async=True, autocommit=True)
            time.sleep(0.1)

        self.assertEqual(status, True)
        self.assertEqual(transaction_id, None)

        self.assertEqual(bank_client.cmd_balance(account_id=666), 1)

    def test_change_balance__sync(self):
        with self.check_delta(lambda: bank_client.cmd_balance(account_id=666), 2):
            status, transaction_id = bank_client.cmd_change_balance(account_id=666, type='test', energy=2, async=False, autocommit=True)

        self.assertEqual(status, True)
        self.assertNotEqual(transaction_id, None)

    def test_change_balance__sync__no_energy(self):
        with self.check_not_changed(lambda: bank_client.cmd_balance(account_id=666)):
            status, transaction_id = bank_client.cmd_change_balance(account_id=666, type='test', energy=-100500, async=False, autocommit=True)

        self.assertEqual(status, False)
        self.assertEqual(transaction_id, None)

    def test_balance__no_balance(self):
        self.assertEqual(bank_client.cmd_balance(account_id=666), 0)

    def test_balance__has_balance(self):
        bank_client.cmd_change_balance(account_id=666, type='test', energy=3, async=False, autocommit=True)
        self.assertEqual(bank_client.cmd_balance(account_id=666), 3)

    def test_commit_transaction(self):
        bank_client.cmd_change_balance(account_id=666, type='test', energy=100, async=False, autocommit=True)

        status, transaction_id = bank_client.cmd_change_balance(account_id=666, type='test', energy=10, async=False, autocommit=False)

        self.assertEqual(bank_client.cmd_balance(account_id=666), 100)

        bank_client.cmd_commit_transaction(transaction_id)

        time.sleep(0.1)

        self.assertEqual(bank_client.cmd_balance(account_id=666), 110)
