# coding: utf-8

from accounts.payments.postponed_tasks import BuyPermanentPurchase
from accounts.payments.tests.base_buy_task_tests import BaseBuyPosponedTaskTests as _BaseBuyPosponedTaskTests
from accounts.payments.relations import PERMANENT_PURCHASE_TYPE

class BuyPermanentPurchasePosponedTaskTests(_BaseBuyPosponedTaskTests):

    def setUp(self):
        super(BuyPermanentPurchasePosponedTaskTests, self).setUp()
        self.purchase_type = PERMANENT_PURCHASE_TYPE.CLAN_OWNERSHIP_RIGHT

        self.task = BuyPermanentPurchase(account_id=self.account.id,
                                         purchase_type=self.purchase_type,
                                         transaction=self.transaction)

    def _test_create(self):
        self.assertEqual(self.task.purchase_type, self.purchase_type)

    def _test_process__transaction_requested__invoice_unprocessed(self):
        self.account.reload()
        self.assertFalse(self.purchase_type in self.account.permanent_purchases)

    def _test_process__transaction_requested__invoice_rejected(self):
        self.account.reload()
        self.assertFalse(self.purchase_type in self.account.permanent_purchases)

    def _test_process__transaction_requested__invoice_wrong_state(self):
        self.account.reload()
        self.assertFalse(self.purchase_type in self.account.permanent_purchases)

    def _test_process__transaction_requested__invoice_frozen(self):
        self.account.reload()
        self.assertFalse(self.purchase_type in self.account.permanent_purchases)

    def _test_process__transaction_frozen(self):
        self.account.reload()
        self.assertTrue(self.purchase_type in self.account.permanent_purchases)

    def _test_process__wrong_state(self):
        self.account.reload()
        self.assertFalse(self.purchase_type in self.account.permanent_purchases)
