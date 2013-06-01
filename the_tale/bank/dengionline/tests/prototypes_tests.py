# coding: utf-8
import urlparse

from datetime import timedelta
from decimal import Decimal

import mock

from common.utils import testcase

from bank.dengionline.prototypes import InvoicePrototype
from bank.dengionline.relations import INVOICE_STATE
from bank.dengionline.conf import dengionline_settings
from bank.dengionline import exceptions
from bank.dengionline.tests.helpers import TestInvoiceFabric

def exception_producer(*argv, **kwargs):
    raise Exception

class InvoicePrototypeTests(testcase.TestCase):

    def setUp(self):
        super(InvoicePrototypeTests, self).setUp()
        self.fabric = TestInvoiceFabric()
        self.invoice = self.fabric.create_invoice()

    def check_raw_invoice(self, state=INVOICE_STATE.REQUESTED):
        self.assertEqual(self.invoice.state, state)
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

    def check_confirmed_invoice(self, state=INVOICE_STATE.CONFIRMED):
        self.assertEqual(self.invoice.state, state)
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

    def test_confim__wrong_order_id(self):
        self.assertTrue(self.invoice.confirm(**self.fabric.confirm_args(order_id=self.invoice.id+1))._is_WRONG_ORDER_ID)
        self.check_raw_invoice()

    def test_confim__wrong_user_id(self):
        self.assertTrue(self.invoice.confirm(**self.fabric.confirm_args(order_id=self.invoice.id, user_id=self.fabric.user_id + u'!'))._is_WRONG_USER_ID)
        self.check_raw_invoice()

    def test_confim__key(self):
        self.assertTrue(self.invoice.confirm(**self.fabric.confirm_args(order_id=self.invoice.id, key='bla-bla-wrong-key'))._is_WRONG_HASH_KEY)
        self.check_raw_invoice()

    def test_confim__success(self):
        self.assertTrue(self.invoice.confirm(**self.fabric.confirm_args(order_id=self.invoice.id))._is_CONFIRMED)
        self.check_confirmed_invoice()

    def test_confim__already_confirmed(self):
        self.invoice.confirm(**self.fabric.confirm_args(order_id=self.invoice.id))
        self.assertTrue(self.invoice.confirm(**self.fabric.confirm_args(order_id=self.invoice.id))._is_ALREADY_CONFIRMED)
        self.check_confirmed_invoice()

    def test_confim__already_confirmed__wrong_arguments(self):
        self.invoice.confirm(**self.fabric.confirm_args(order_id=self.invoice.id))
        self.assertTrue(self.invoice.confirm(**self.fabric.confirm_args(order_id=self.invoice.id, paymode=self.fabric.paymode+1))._is_ALREADY_CONFIRMED_WRONG_ARGUMENTS)
        self.check_confirmed_invoice()

    def test_confim__already_processed(self):
        self.invoice.confirm(**self.fabric.confirm_args(order_id=self.invoice.id))
        self.invoice._model.state = INVOICE_STATE.PROCESSED
        self.invoice.save()
        self.assertTrue(self.invoice.confirm(**self.fabric.confirm_args(order_id=self.invoice.id))._is_ALREADY_PROCESSED)
        self.check_confirmed_invoice(state=INVOICE_STATE.PROCESSED)

    def test_confim__already_processed__wrong_arguments(self):
        self.invoice.confirm(**self.fabric.confirm_args(order_id=self.invoice.id))
        self.invoice._model.state = INVOICE_STATE.PROCESSED
        self.invoice.save()
        self.assertTrue(self.invoice.confirm(**self.fabric.confirm_args(order_id=self.invoice.id, paymode=self.fabric.paymode+1))._is_ALREADY_PROCESSED_WRONG_ARGUMENTS)
        self.check_confirmed_invoice(state=INVOICE_STATE.PROCESSED)

    def test_confim__already_failed_on_confirm(self):
        self.invoice.fail_on_confirm()
        self.assertTrue(self.invoice.confirm(**self.fabric.confirm_args(order_id=self.invoice.id))._is_ALREADY_FAILED_ON_CONFIRM)
        self.check_raw_invoice(state=INVOICE_STATE.FAILED_ON_CONFIRM)

    def test_confim__discarded(self):
        self.invoice._model.state = INVOICE_STATE.DISCARDED
        self.invoice.save()
        self.assertTrue(self.invoice.confirm(**self.fabric.confirm_args(order_id=self.invoice.id))._is_DISCARDED)
        self.check_raw_invoice(state=INVOICE_STATE.DISCARDED)

    def test_confirm__all_states_processed_correctly(self):
        for state in INVOICE_STATE._records:
            self.invoice._model.state = state
            self.invoice.save()
            self.invoice.confirm(**self.fabric.confirm_args(order_id=self.invoice.id))

    def test_fail_on_confirm(self):
        self.invoice.fail_on_confirm()
        self.assertTrue(self.invoice.state._is_FAILED_ON_CONFIRM)

    def confirm_payment_args(self, order_id=None, received_amount=None, user_id=None, payment_id=None, key=None, paymode=None):
        if received_amount is None:
            received_amount = self.fabric.received_amount
        if user_id is None:
            user_id = u'%s' % self.fabric.user_id.encode('cp1251')
        if payment_id is None:
            payment_id = self.fabric.payment_id
        if key is None:
            key = InvoicePrototype.confirm_request_key(amount=received_amount, user_id=user_id, payment_id=payment_id)

        return {'order_id': self.invoice.id if order_id is None else order_id,
                'received_amount': received_amount,
                'user_id': user_id,
                'payment_id': payment_id,
                'paymode': self.fabric.paymode if paymode is None else paymode,
                'key': key}

    def test_confirm_payment__invoice_not_found(self):
        self.assertTrue(InvoicePrototype.confirm_payment(**self.confirm_payment_args(order_id=666))._is_INVOICE_NOT_FOUND)

    @mock.patch('bank.dengionline.prototypes.InvoicePrototype.confirm', exception_producer)
    def test_confirm_payment__exception_when_confirm(self):
        self.assertRaises(Exception, InvoicePrototype.confirm_payment, **self.confirm_payment_args())
        self.invoice.reload()
        self.assertTrue(self.invoice.state._is_FAILED_ON_CONFIRM)

    def test_confirm_payment__success(self):
        with mock.patch('bank.dengionline.workers.banker.Worker.cmd_handle_confirmations') as cmd_handle_confirmations:
            self.assertTrue(InvoicePrototype.confirm_payment(**self.confirm_payment_args())._is_CONFIRMED)
        self.assertEqual(cmd_handle_confirmations.call_count, 1)

    def test_discards_old_invoices(self):
        self.assertEqual(InvoicePrototype._db_filter(state=INVOICE_STATE.REQUESTED).count(), 1)
        InvoicePrototype.discard_old_invoices()
        self.assertEqual(InvoicePrototype._db_filter(state=INVOICE_STATE.REQUESTED).count(), 1)

        with mock.patch('bank.dengionline.conf.dengionline_settings.DISCARD_TIMEOUT', timedelta(seconds=0)):
            InvoicePrototype.discard_old_invoices()

        self.assertEqual(InvoicePrototype._db_filter(state=INVOICE_STATE.REQUESTED).count(), 0)
        self.assertEqual(InvoicePrototype._db_filter(state=INVOICE_STATE.DISCARDED).count(), 1)

    def test_process(self):
        from bank.prototypes import InvoicePrototype as BankInvoicePrototype

        self.assertEqual(BankInvoicePrototype._db_count(), 0)

        self.assertRaises(exceptions.WrongInvoiceStateInProcessingError, self.invoice.process)

        self.assertEqual(BankInvoicePrototype._db_count(), 0)

        self.invoice.confirm(**self.fabric.confirm_args(order_id=self.invoice.id))

        self.assertEqual(BankInvoicePrototype._db_count(), 0)

        self.invoice.process()

        self.assertEqual(BankInvoicePrototype._db_count(), 1)
        self.assertTrue(BankInvoicePrototype._db_get_object(0).state._is_FORCED)
