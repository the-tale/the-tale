# coding: utf-8

from the_tale.finances.shop.postponed_tasks import BuyPermanentPurchase
from the_tale.finances.shop.tests import base_buy_task
from the_tale.finances.shop.relations import PERMANENT_PURCHASE_TYPE

class BuyPermanentPurchasePosponedTaskTests(base_buy_task._BaseBuyPosponedTaskTests):

    def setUp(self):
        super(BuyPermanentPurchasePosponedTaskTests, self).setUp()
        self.purchase_type = PERMANENT_PURCHASE_TYPE.CLAN_OWNERSHIP_RIGHT

        self.task = BuyPermanentPurchase(account_id=self.account.id,
                                         purchase_type=self.purchase_type,
                                         transaction=self.transaction)

        self.cmd_update_with_account_data__call_count = 0 # no need in updating hero state



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
