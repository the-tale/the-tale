# coding: utf-8

from common.utils import testcase

from bank.relations import ENTITY_TYPE as BANK_ENTITY_TYPE, CURRENCY_TYPE as BANK_CURRENCY_TYPE

from bank.dengionline.prototypes import InvoicePrototype
from bank.dengionline.transaction import Transaction
from bank.dengionline.relations import CURRENCY_TYPE


class TransactionTests(testcase.TestCase):

    def setUp(self):
        super(TransactionTests, self).setUp()

        self.bank_type = BANK_ENTITY_TYPE.GAME_ACCOUNT
        self.bank_id = 2
        self.bank_currency = BANK_CURRENCY_TYPE.PREMIUM
        self.bank_amount = 13

        self.email = 'test@test.com'
        self.comment = u'оплата какой-то покупки'
        self.payment_amount = 10
        self.payment_currency = CURRENCY_TYPE.USD
        self.received_amount = 66
        self.received_currency = CURRENCY_TYPE.RUB
        self.payment_id = 12345
        self.paymode = 22

    def create_transaction(self):
        return Transaction.create(bank_type=self.bank_type,
                                  bank_id=self.bank_id,
                                  bank_currency=self.bank_currency,
                                  bank_amount=self.bank_amount,
                                  email=self.email,
                                  comment=self.comment,
                                  payment_amount=self.payment_amount,
                                  payment_currency=self.payment_currency)


    def test_create(self):
        transaction = self.create_transaction()
        invoice = InvoicePrototype.get_by_id(transaction.invoice_id)

        self.assertTrue(invoice.state._is_REQUESTED)
        self.assertEqual(invoice.bank_type, self.bank_type)
        self.assertEqual(invoice.bank_id, self.bank_id)
        self.assertEqual(invoice.bank_currency, self.bank_currency)
        self.assertEqual(invoice.bank_amount, self.bank_amount)
        self.assertEqual(invoice.user_id, self.email)
        self.assertEqual(invoice.comment, self.comment)
        self.assertEqual(invoice.payment_amount, self.payment_amount)
        self.assertEqual(invoice.payment_currency, self.payment_currency)
        self.assertEqual(invoice.received_amount, None)
        self.assertEqual(invoice.received_currency, None)
        self.assertEqual(invoice.paymode, None)
        self.assertEqual(invoice.payment_id, None)

    def get_simple_payment_url(self):
        transaction = self.create_transaction()
        invoice = InvoicePrototype.get_by_id(transaction.invoice_id)

        self.assertEqual(invoice.simple_payment_url, 'https://paymentgateway.ru/?orderid=1&comment=%EE%EF%EB%E0%F2%E0+%EA%E0%EA%EE%E9-%F2%EE+%EF%EE%EA%F3%EF%EA%E8&project=TEST-PROJECT-ID&source=TEST-PROJECT-ID&amount=10&paymentCurrency=USD&nickname=test%40test.com')
