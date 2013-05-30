# coding: utf-8
import urlparse
from decimal import Decimal

from common.utils import testcase

from bank.dengionline.prototypes import InvoicePrototype
from bank.dengionline.relations import INVOICE_STATE
from bank.dengionline import exceptions
from bank.dengionline.conf import dengionline_settings

from bank.dengionline.tests.helpers import TestInvoiceFabric


class InvoicePrototypeTests(testcase.TestCase):

    def setUp(self):
        super(InvoicePrototypeTests, self).setUp()
        self.fabric = TestInvoiceFabric()
        self.invoice = self.fabric.create_invoice()

    def check_raw_invoice(self):
        self.assertTrue(self.invoice.state._is_REQUESTED)
        self.assertEqual(self.invoice.bank_type, self.fabric.bank_type)
        self.assertEqual(self.invoice.bank_id, self.fabric.bank_id)
        self.assertEqual(self.invoice.bank_currency, self.fabric.bank_currency)
        self.assertEqual(self.invoice.bank_amount, self.fabric.bank_amount)
        self.assertEqual(self.invoice.user_id, self.fabric.user_id)
        self.assertEqual(self.invoice.comment, self.fabric.comment)
        self.assertEqual(self.invoice.payment_amount, self.fabric.payment_amount)
        self.assertEqual(self.invoice.payment_currency, self.fabric.payment_currency)
        self.assertEqual(self.invoice.received_amount, None)
        self.assertEqual(self.invoice.received_currency, None)
        self.assertEqual(self.invoice.paymode, None)
        self.assertEqual(self.invoice.payment_id, None)

    def check_confirmed_invoice(self):
        self.assertTrue(self.invoice.state._is_CONFIRMED)
        self.assertEqual(self.invoice.bank_type, self.fabric.bank_type)
        self.assertEqual(self.invoice.bank_id, self.fabric.bank_id)
        self.assertEqual(self.invoice.bank_currency, self.fabric.bank_currency)
        self.assertEqual(self.invoice.bank_amount, self.fabric.bank_amount)
        self.assertEqual(self.invoice.user_id, self.fabric.user_id)
        self.assertEqual(self.invoice.comment, self.fabric.comment)
        self.assertEqual(self.invoice.payment_amount, self.fabric.payment_amount)
        self.assertEqual(self.invoice.payment_currency, self.fabric.payment_currency)
        self.assertEqual(self.invoice.received_amount, self.fabric.received_amount)
        self.assertEqual(self.invoice.received_currency, self.fabric.received_currency)
        self.assertEqual(self.invoice.paymode, self.fabric.paymode)
        self.assertEqual(self.invoice.payment_id, self.fabric.payment_id)

    def test_create(self):
        self.check_raw_invoice()

    def test_payment_id(self):
        self.assertEqual(self.invoice.payment_id, None)
        self.invoice._model.payment_id = '123456'
        self.assertEqual(self.invoice.payment_id, 123456)

    def test_simple_payment_url(self):
        parsed_url = urlparse.urlparse(self.invoice.simple_payment_url)
        self.assertEqual(parsed_url.netloc, 'paymentgateway.ru')

        self.assertEqual(urlparse.parse_qs(parsed_url.query), { 'orderid': [str(self.invoice.id)],
                                                                'comment': [self.fabric.comment.encode('cp1251')],
                                                                'project': [dengionline_settings.PROJECT_ID],
                                                                'source': [dengionline_settings.PROJECT_ID],
                                                                'amount': [str(self.fabric.payment_amount)],
                                                                'paymentCurrency': [self.fabric.payment_currency.url_code],
                                                                'nickname': [self.fabric.user_id]})

    def test_confirm_request_key(self):
        self.assertEqual(self.invoice.confirm_request_key(amount=Decimal('666.22'), user_id=u'идентификатор', payment_id=666), '6b62913410ef3a8c788ef05042d3a7c3')

    def test_check_user_request_key(self):
        self.assertEqual(self.invoice.check_user_request_key(user_id=u'идентификатор'), '078472915f9029eb178a69283db86966')

    def test_check_user__wrong_key(self):
        self.assertTrue(InvoicePrototype.check_user(user_id=self.invoice.user_id, key='bla-bla')._is_WRONG_KEY)

    def test_check_user__user_exists(self):
        self.assertTrue(InvoicePrototype.check_user(user_id=self.invoice.user_id, key='c38fc225fe78889420e0242350bbeb45')._is_USER_EXISTS)

    def test_check_user__user_not_exists(self):
        for state in INVOICE_STATE._records:
            if state._is_REQUESTED:
                continue
            self.invoice._model.state = state
            self.invoice.save()
            self.assertTrue(InvoicePrototype.check_user(user_id=self.invoice.user_id, key='c38fc225fe78889420e0242350bbeb45')._is_USER_NOT_EXISTS)

    def confirm_args(self, order_id=None, received_amount=None, received_currency=None, user_id=None, payment_id=None, key=None, paymode=None):
        if received_amount is None:
            received_amount = self.fabric.received_amount
        if user_id is None:
            user_id = self.fabric.user_id
        if payment_id is None:
            payment_id = self.fabric.payment_id
        if key is None:
            key = InvoicePrototype.confirm_request_key(amount=received_amount, user_id=user_id, payment_id=payment_id)

        return {'order_id': self.invoice.id if order_id is None else order_id,
                'received_amount': received_amount,
                'received_currency': self.fabric.received_currency if received_currency is None else received_currency,
                'user_id': user_id,
                'payment_id': payment_id,
                'paymode': self.fabric.paymode if paymode is None else paymode,
                'key': key}


    def test_confim__wrong_order_id(self):
        self.assertRaises(exceptions.WrongOrderIdInConfirmationError,
                          self.invoice.confirm, **self.confirm_args(order_id=self.invoice.id+1))
        self.check_raw_invoice()

    def test_confim__wrong_user_id(self):
        self.assertRaises(exceptions.WrongUserIdInConfirmationError,
                          self.invoice.confirm, **self.confirm_args(user_id=self.fabric.user_id + u'!'))
        self.check_raw_invoice()

    def test_confim__key(self):
        self.assertRaises(exceptions.WrongRequestKeyInConfirmationError,
                          self.invoice.confirm, **self.confirm_args(key='bla-bla-wrong-key'))
        self.check_raw_invoice()

    def test_confim__success(self):
        self.invoice.confirm(**self.confirm_args())
        self.check_confirmed_invoice()

    def test_confim__already_confirmed(self):
        self.invoice.confirm(**self.confirm_args())
        self.assertRaises(exceptions.InvoiceAlreadyConfirmedError,
                          self.invoice.confirm, **self.confirm_args())
        self.check_confirmed_invoice()
