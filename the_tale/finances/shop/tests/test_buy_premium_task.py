# coding: utf-8

import datetime

from the_tale.finances.shop.postponed_tasks import BuyPremium
from the_tale.finances.shop.tests import base_buy_task


class BuyPremiumPosponedTaskTests(base_buy_task._BaseBuyPosponedTaskTests):

    def setUp(self):
        super(BuyPremiumPosponedTaskTests, self).setUp()
        self.days = 13

        self.task = BuyPremium(account_id=self.account.id,
                               days=self.days,
                               transaction=self.transaction)

    def _test_create(self):
        self.assertEqual(self.task.days, self.days)

    def _test_process__transaction_requested__invoice_unprocessed(self):
        self.account.reload()
        self.assertTrue(self.account.premium_end_at < datetime.datetime.now())

    def _test_process__transaction_requested__invoice_rejected(self):
        self.account.reload()
        self.assertTrue(self.account.premium_end_at < datetime.datetime.now())

    def _test_process__transaction_requested__invoice_wrong_state(self):
        self.account.reload()
        self.assertTrue(self.account.premium_end_at < datetime.datetime.now())

    def _test_process__transaction_requested__invoice_frozen(self):
        self.account.reload()
        self.assertTrue(self.account.premium_end_at < datetime.datetime.now())

    def _test_process__transaction_frozen(self):
        self.account.reload()
        self.assertTrue(self.account.premium_end_at > datetime.datetime.now())
        self.assertTrue(datetime.datetime.now() + datetime.timedelta(days=self.days-1) < self.account.premium_end_at)
        self.assertTrue(datetime.datetime.now() + datetime.timedelta(days=self.days+1) > self.account.premium_end_at)

    def _test_process__wrong_state(self):
        self.account.reload()
        self.assertTrue(self.account.premium_end_at < datetime.datetime.now())
