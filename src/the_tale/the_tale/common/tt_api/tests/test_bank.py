
import smart_imports

smart_imports.all()


bank_client = bank.Client(entry_point=game_conf.settings.TT_ENERGY_ENTRY_POINT,
                          transaction_lifetime=60)


class FakeBalanceError(Exception):
    pass


fake_banker = bank_client.banker(change_balance_error=FakeBalanceError)


class TTBankAPiTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        bank_client.cmd_debug_clear_service()

    def test_change_balance__no_autocommit_in_async_request(self):
        with self.assertRaises(exceptions.AutocommitRequiredForAsyncTransaction):
            bank_client.cmd_change_balance(account_id=666, type='test', amount=1, async=True, autocommit=False)

    def test_change_balance__async(self):
        with self.check_delta(lambda: bank_client.cmd_balance(account_id=666), 1):
            status, transaction_id = bank_client.cmd_change_balance(account_id=666, type='test', amount=1, async=True, autocommit=True)
            time.sleep(0.1)

        self.assertEqual(status, True)
        self.assertEqual(transaction_id, None)

        self.assertEqual(bank_client.cmd_balance(account_id=666), 1)

    def test_change_balance__sync(self):
        with self.check_delta(lambda: bank_client.cmd_balance(account_id=666), 2):
            status, transaction_id = bank_client.cmd_change_balance(account_id=666, type='test', amount=2, async=False, autocommit=True)

        self.assertEqual(status, True)
        self.assertNotEqual(transaction_id, None)

    def test_change_balance__sync__no_amount(self):
        with self.check_not_changed(lambda: bank_client.cmd_balance(account_id=666)):
            status, transaction_id = bank_client.cmd_change_balance(account_id=666, type='test', amount=-100500, async=False, autocommit=True)

        self.assertEqual(status, False)
        self.assertEqual(transaction_id, None)

    def test_change_balance__restrictions(self):
        with self.check_delta(lambda: bank_client.cmd_balance(account_id=666), 103):
            status, transaction_id = bank_client.cmd_change_balance(account_id=666,
                                                                    type='test',
                                                                    amount=200,
                                                                    async=False,
                                                                    autocommit=True,
                                                                    restrictions=bank_client.Restrictions(soft_maximum=103))

        self.assertEqual(status, True)
        self.assertNotEqual(transaction_id, None)

    def test_balance__no_balance(self):
        self.assertEqual(bank_client.cmd_balance(account_id=666), 0)

    def test_balance__has_balance(self):
        bank_client.cmd_change_balance(account_id=666, type='test', amount=3, async=False, autocommit=True)
        self.assertEqual(bank_client.cmd_balance(account_id=666), 3)

    def test_balances__complext(self):
        bank_client.cmd_change_balance(account_id=666, type='test', amount=3, currency=0, async=False, autocommit=True)
        bank_client.cmd_change_balance(account_id=777, type='test', amount=4, currency=0, async=False, autocommit=True)
        bank_client.cmd_change_balance(account_id=666, type='test', amount=5, currency=1, async=False, autocommit=True)
        bank_client.cmd_change_balance(account_id=888, type='test', amount=6, currency=0, async=False, autocommit=True)

        self.assertEqual(bank_client.cmd_balances(accounts_ids=(666, 777)),
                         {666: {0: 3, 1: 5},
                          777: {0: 4}})

    def test_commit_transaction(self):
        bank_client.cmd_change_balance(account_id=666, type='test', amount=100, async=False, autocommit=True)

        status, transaction_id = bank_client.cmd_change_balance(account_id=666, type='test', amount=10, async=False, autocommit=False)

        self.assertEqual(bank_client.cmd_balance(account_id=666), 100)

        bank_client.cmd_commit_transaction(transaction_id)

        time.sleep(0.1)

        self.assertEqual(bank_client.cmd_balance(account_id=666), 110)

    def test_rollback_transaction(self):
        bank_client.cmd_change_balance(account_id=666, type='test', amount=100, async=False, autocommit=True)

        status, transaction_id = bank_client.cmd_change_balance(account_id=666, type='test', amount=10, async=False, autocommit=False)

        self.assertEqual(bank_client.cmd_balance(account_id=666), 100)

        bank_client.cmd_rollback_transaction(transaction_id)

        time.sleep(0.1)

        self.assertEqual(bank_client.cmd_balance(account_id=666), 100)

    def test_banker__balance_error(self):
        bank_client.cmd_change_balance(account_id=666, type='test', amount=100, async=False, autocommit=True)

        with self.assertRaises(FakeBalanceError):
            with fake_banker(account_id=666, type='test', amount=-110):
                pass

        time.sleep(0.1)

        self.assertEqual(bank_client.cmd_balance(account_id=666), 100)

    def test_banker__success(self):
        bank_client.cmd_change_balance(account_id=666, type='test', amount=100, async=False, autocommit=True)

        with fake_banker(account_id=666, type='test', amount=-10):
            pass

        time.sleep(0.1)

        self.assertEqual(bank_client.cmd_balance(account_id=666), 90)

    def test_banker__error_while_processing(self):
        bank_client.cmd_change_balance(account_id=666, type='test', amount=100, async=False, autocommit=True)

        with self.assertRaises(Exception):
            with fake_banker(account_id=666, type='test', amount=-10):
                raise Exception('!')

        time.sleep(0.1)

        self.assertEqual(bank_client.cmd_balance(account_id=666), 100)

    def test_transaction_lifetime_redefining(self):
        bank_client.cmd_change_balance(account_id=666,
                                       type='test',
                                       amount=100,
                                       async=False,
                                       autocommit=True)

        transaction_lifetime = 1

        status, transaction_id = bank_client.cmd_change_balance(account_id=666,
                                                                type='test',
                                                                amount=10,
                                                                async=False,
                                                                autocommit=False,
                                                                transaction_lifetime=transaction_lifetime)

        self.assertEqual(bank_client.cmd_balance(account_id=666), 100)

        time.sleep(transaction_lifetime + 1)

        with self.assertRaises(exceptions.TTAPIUnexpectedAPIStatus):
            bank_client.cmd_commit_transaction(transaction_id)

        time.sleep(0.1)

        self.assertEqual(bank_client.cmd_balance(account_id=666), 100)
