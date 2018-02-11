# coding: utf-8

from unittest import mock

from the_tale.common.utils import testcase

from the_tale.common.postponed_tasks.prototypes import PostponedTaskPrototype

from the_tale.finances.bank.prototypes import InvoicePrototype
from the_tale.finances.bank.relations import ENTITY_TYPE, CURRENCY_TYPE

from the_tale.game.logic import create_test_map

from the_tale.accounts.clans.conf import clans_settings

from the_tale.game.heroes import logic as heroes_logic

from the_tale.finances.shop.postponed_tasks import BuyPremium, BuyPermanentPurchase
from the_tale.finances.shop.goods import PremiumDays, PermanentPurchase
from the_tale.finances.shop import exceptions
from the_tale.finances.shop.relations import PERMANENT_PURCHASE_TYPE
from the_tale.finances.shop.conf import payments_settings


class PremiumDaysTests(testcase.TestCase):

    def setUp(self):
        super(PremiumDaysTests, self).setUp()

        create_test_map()

        self.days = 30
        self.cost = 130

        self.account = self.accounts_factory.create_account()

        self.hero = heroes_logic.load_hero(account_id=self.account.id)

        self.purchase = PremiumDays(uid='premium-days-uid',
                                    name='premium-days-name',
                                    description='premium-days-description',
                                    cost=self.cost,
                                    days=self.days,
                                    transaction_description='premium-days-transaction-description')

    def test_create(self):
        self.assertEqual(self.purchase.uid, 'premium-days-uid')
        self.assertEqual(self.purchase.days, self.days)
        self.assertEqual(self.purchase.cost, self.cost)
        self.assertEqual(self.purchase.name, 'premium-days-name')
        self.assertEqual(self.purchase.description, 'premium-days-description')
        self.assertEqual(self.purchase.transaction_description, 'premium-days-transaction-description')

    def test_buy__fast_account(self):
        self.assertEqual(PostponedTaskPrototype._model_class.objects.all().count(), 0)
        self.assertEqual(InvoicePrototype._model_class.objects.all().count(), 0)

        self.account.is_fast = True
        self.account.save()

        self.assertRaises(exceptions.FastAccountError, self.purchase.buy, account=self.account)

        self.assertEqual(PostponedTaskPrototype._model_class.objects.all().count(), 0)
        self.assertEqual(InvoicePrototype._model_class.objects.all().count(), 0)


    def test_buy(self):
        self.assertEqual(PostponedTaskPrototype._model_class.objects.all().count(), 0)
        self.assertEqual(InvoicePrototype._model_class.objects.all().count(), 0)

        with mock.patch('the_tale.common.postponed_tasks.prototypes.PostponedTaskPrototype.cmd_wait') as cmd_wait:
            self.purchase.buy(account=self.account)

        self.assertEqual(cmd_wait.call_count, 1)

        self.assertEqual(PostponedTaskPrototype._model_class.objects.all().count(), 1)
        self.assertEqual(InvoicePrototype._model_class.objects.all().count(), 1)

        postponed_logic = PostponedTaskPrototype._db_get_object(0).internal_logic

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
        self.assertEqual(invoice.description_for_sender, 'premium-days-transaction-description')
        self.assertEqual(invoice.description_for_recipient, 'premium-days-transaction-description')


    def test_is_purchasable(self):
        self.assertTrue(self.purchase.is_purchasable(self.account, self.hero))

    def test_is_purchasable__premium(self):
        self.account.prolong_premium(30)
        self.assertTrue(self.purchase.is_purchasable(self.account, self.hero))



class PermanentPurchaseTests(testcase.TestCase):

    PURCHASE_TYPE = PERMANENT_PURCHASE_TYPE.INFINIT_SUBSCRIPTION

    def setUp(self):
        super(PermanentPurchaseTests, self).setUp()

        create_test_map()

        self.cost = 130

        self.account = self.accounts_factory.create_account()
        self.hero = heroes_logic.load_hero(account_id=self.account.id)

        self.purchase = PermanentPurchase(uid='infinit-subscription',
                                          name=self.PURCHASE_TYPE.text,
                                          description=self.PURCHASE_TYPE.description,
                                          cost=self.cost,
                                          purchase_type=self.PURCHASE_TYPE,
                                          transaction_description='infinit-subscription')


    def test_create(self):
        self.assertEqual(self.purchase.uid, 'infinit-subscription')
        self.assertEqual(self.purchase.purchase_type, self.PURCHASE_TYPE)
        self.assertEqual(self.purchase.cost, self.cost)
        self.assertEqual(self.purchase.name, self.PURCHASE_TYPE.text)
        self.assertEqual(self.purchase.description, self.PURCHASE_TYPE.description)
        self.assertEqual(self.purchase.transaction_description, 'infinit-subscription')

    def test_buy__fast_account(self):
        self.assertEqual(PostponedTaskPrototype._model_class.objects.all().count(), 0)
        self.assertEqual(InvoicePrototype._model_class.objects.all().count(), 0)

        self.account.is_fast = True
        self.account.save()

        self.assertRaises(exceptions.FastAccountError, self.purchase.buy, account=self.account)

        self.assertEqual(PostponedTaskPrototype._model_class.objects.all().count(), 0)
        self.assertEqual(InvoicePrototype._model_class.objects.all().count(), 0)


    def test_buy(self):
        self.assertEqual(PostponedTaskPrototype._model_class.objects.all().count(), 0)
        self.assertEqual(InvoicePrototype._model_class.objects.all().count(), 0)

        with mock.patch('the_tale.common.postponed_tasks.prototypes.PostponedTaskPrototype.cmd_wait') as cmd_wait:
            self.purchase.buy(account=self.account)

        self.assertEqual(cmd_wait.call_count, 1)

        self.assertEqual(PostponedTaskPrototype._model_class.objects.all().count(), 1)
        self.assertEqual(InvoicePrototype._model_class.objects.all().count(), 1)

        postponed_logic = PostponedTaskPrototype._db_get_object(0).internal_logic

        self.assertTrue(isinstance(postponed_logic, BuyPermanentPurchase))
        self.assertEqual(postponed_logic.account_id, self.account.id)
        self.assertEqual(postponed_logic.purchase_type, self.PURCHASE_TYPE)

        invoice = InvoicePrototype.get_by_id(postponed_logic.transaction.invoice_id)

        self.assertEqual(invoice.recipient_type, ENTITY_TYPE.GAME_ACCOUNT)
        self.assertEqual(invoice.recipient_id, self.account.id)
        self.assertEqual(invoice.sender_type, ENTITY_TYPE.GAME_LOGIC)
        self.assertEqual(invoice.sender_id, 0)
        self.assertEqual(invoice.currency, CURRENCY_TYPE.PREMIUM)
        self.assertEqual(invoice.amount, -self.cost)
        self.assertEqual(invoice.description_for_sender, 'infinit-subscription')
        self.assertEqual(invoice.description_for_recipient, 'infinit-subscription')

    def test_is_purchasable(self):
        self.assertTrue(self.purchase.is_purchasable(self.account, self.hero))

    def test_is_purchasable__already_purchased(self):
        self.account.permanent_purchases.insert(self.PURCHASE_TYPE)
        self.assertFalse(self.purchase.is_purchasable(self.account, self.hero))
