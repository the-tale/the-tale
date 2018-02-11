
import time

from the_tale.common.utils import testcase

from .. import exceptions
from .. import tt_api


class TTBankAPiTests(testcase.TestCase):

    def setUp(self):
        super().setUp()
        tt_api.debug_clear_service()

    def test_change_energy_balance__no_autocommit_in_async_request(self):
        with self.assertRaises(exceptions.AutocommitRequiredForAsyncTransaction):
            tt_api.change_energy_balance(account_id=666, type='test', energy=1, async=True, autocommit=False)

    def test_change_energy_balance__async(self):
        with self.check_delta(lambda: tt_api.energy_balance(account_id=666), 1):
            status, transaction_id = tt_api.change_energy_balance(account_id=666, type='test', energy=1, async=True, autocommit=True)
            time.sleep(0.1)

        self.assertEqual(status, True)
        self.assertEqual(transaction_id, None)

        self.assertEqual(tt_api.energy_balance(account_id=666), 1)

    def test_change_energy_balance__sync(self):
        with self.check_delta(lambda: tt_api.energy_balance(account_id=666), 2):
            status, transaction_id = tt_api.change_energy_balance(account_id=666, type='test', energy=2, async=False, autocommit=True)

        self.assertEqual(status, True)
        self.assertNotEqual(transaction_id, None)

    def test_change_energy_balance__sync__no_energy(self):
        with self.check_not_changed(lambda: tt_api.energy_balance(account_id=666)):
            status, transaction_id = tt_api.change_energy_balance(account_id=666, type='test', energy=-100500, async=False, autocommit=True)

        self.assertEqual(status, False)
        self.assertEqual(transaction_id, None)

    def test_balance__no_balance(self):
        self.assertEqual(tt_api.energy_balance(account_id=666), 0)

    def test_balance__has_balance(self):
        tt_api.change_energy_balance(account_id=666, type='test', energy=3, async=False, autocommit=True)
        self.assertEqual(tt_api.energy_balance(account_id=666), 3)

    def test_commit_transaction(self):
        tt_api.change_energy_balance(account_id=666, type='test', energy=100, async=False, autocommit=True)

        status, transaction_id = tt_api.change_energy_balance(account_id=666, type='test', energy=10, async=False, autocommit=False)

        self.assertEqual(tt_api.energy_balance(account_id=666), 100)

        tt_api.commit_transaction(transaction_id)

        time.sleep(0.1)

        self.assertEqual(tt_api.energy_balance(account_id=666), 110)
