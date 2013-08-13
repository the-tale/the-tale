# coding: utf-8

from accounts.payments.postponed_tasks import BuyEnergyCharges
from accounts.payments.tests.base_buy_task_tests import BaseBuyPosponedTaskTests as _BaseBuyPosponedTaskTests

from game.logic_storage import LogicStorage


class BuyEnergyChargesTaskTests(_BaseBuyPosponedTaskTests):

    def setUp(self):
        super(BuyEnergyChargesTaskTests, self).setUp()
        self.charges_number = 13

        self.task = BuyEnergyCharges(account_id=self.account.id,
                                     charges_number=self.charges_number,
                                     transaction=self.transaction)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.cmd_update_with_account_data__call_count = 0
        self.accounts_manages_worker = False
        self.supervisor_worker = True

        self.hero = self.storage.accounts_to_heroes[self.account.id]
        self.hero.energy_charges = 0


    def _test_create(self):
        self.assertEqual(self.task.charges_number, self.charges_number)

    def _test_process__transaction_requested__invoice_unprocessed(self):
        self.assertEqual(self.hero.energy_charges, 0)

    def _test_process__transaction_requested__invoice_rejected(self):
        self.assertEqual(self.hero.energy_charges, 0)

    def _test_process__transaction_requested__invoice_wrong_state(self):
        self.assertEqual(self.hero.energy_charges, 0)

    def _test_process__transaction_requested__invoice_frozen(self):
        self.assertEqual(self.hero.energy_charges, 0)

    def _test_process__transaction_frozen(self):
        self.assertEqual(self.hero.energy_charges, self.charges_number)

    def _test_process__wrong_state(self):
        self.assertEqual(self.hero.energy_charges, 0)
