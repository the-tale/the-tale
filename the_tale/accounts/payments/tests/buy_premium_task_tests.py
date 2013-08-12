# coding: utf-8

import datetime

from accounts.payments.postponed_tasks import BuyPremium
from accounts.payments.tests.base_buy_task_tests import BaseBuyPosponedTaskTests as _BaseBuyPosponedTaskTests


class BuyPremiumPosponedTaskTests(_BaseBuyPosponedTaskTests):

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
