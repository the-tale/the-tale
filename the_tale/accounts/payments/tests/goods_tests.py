# coding: utf-8

import mock

from common.utils import testcase

from common.postponed_tasks import PostponedTaskPrototype, autodiscover

from bank.prototypes import InvoicePrototype
from bank.relations import ENTITY_TYPE, CURRENCY_TYPE

from game.logic import create_test_map

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from accounts.payments.postponed_tasks import BuyPremium

from accounts.payments.goods import PremiumDays


class PremiumDaysTests(testcase.TestCase):

    def setUp(self):
        super(PremiumDaysTests, self).setUp()

        autodiscover()

        create_test_map()

        self.days = 30
        self.cost = 130

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)

        self.purchase = PremiumDays(uid='premium-days-uid',
                                    name=u'premium-days-name',
                                    description=u'premium-days-description',
                                    cost=self.cost,
                                    days=self.days,
                                    transaction_description='premium-days-transaction-description')

    def test_create(self):
        self.assertEqual(self.purchase.uid, 'premium-days-uid')
        self.assertEqual(self.purchase.days, self.days)
        self.assertEqual(self.purchase.cost, self.cost)
        self.assertEqual(self.purchase.name, u'premium-days-name')
        self.assertEqual(self.purchase.description, u'premium-days-description')
        self.assertEqual(self.purchase.transaction_description, u'premium-days-transaction-description')

    def test_buy(self):
        self.assertEqual(PostponedTaskPrototype._model_class.objects.all().count(), 0)
        self.assertEqual(InvoicePrototype._model_class.objects.all().count(), 0)

        with mock.patch('common.postponed_tasks.PostponedTaskPrototype.cmd_wait') as cmd_wait:
            self.purchase.buy(account_id=self.account.id)

        self.assertEqual(cmd_wait.call_count, 1)

        self.assertEqual(PostponedTaskPrototype._model_class.objects.all().count(), 1)
        self.assertEqual(InvoicePrototype._model_class.objects.all().count(), 1)

        postponed_logic = PostponedTaskPrototype._get_object(0).internal_logic

        self.assertTrue(isinstance(postponed_logic, BuyPremium))
        self.assertEqual(postponed_logic.account_id, self.account.id)
        self.assertEqual(postponed_logic.days, self.days)

        invoice = InvoicePrototype.get_by_id(postponed_logic.transaction.invoice_id)

        self.assertEqual(invoice.recipient_type, ENTITY_TYPE.GAME_ACCOUNT)
        self.assertEqual(invoice.recipient_id, self.account.id)
        self.assertEqual(invoice.sender_type, ENTITY_TYPE.GAME_LOGIC)
        self.assertEqual(invoice.sender_id, 0)
        self.assertEqual(invoice.currency, CURRENCY_TYPE.PREMIUM)
        self.assertEqual(invoice.amount, -self.cost)
        self.assertEqual(invoice.description, u'premium-days-transaction-description')
