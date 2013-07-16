# coding: utf-8
import mock

from common.utils import testcase

from bank.prototypes import InvoicePrototype as BankInvoicePrototype

from bank.xsolla.prototypes import InvoicePrototype
from bank.xsolla.relations import INVOICE_STATE
from bank.xsolla import exceptions

from bank.xsolla.tests.helpers import TestInvoiceFabric


class InvoicePrototypeTests(testcase.TestCase):

    def setUp(self):
        super(InvoicePrototypeTests, self).setUp()
        self.fabric = TestInvoiceFabric()

    def create_invoice(self, worker_call_count, **kwargs):
        with mock.patch('bank.xsolla.workers.banker.Worker.cmd_handle_invoices') as cmd_handle_invoices:
            invoice = self.fabric.create_invoice(**kwargs)

        self.assertEqual(cmd_handle_invoices.call_count, worker_call_count)

        return invoice

    def pay(self, worker_call_count, **kwargs):
        self.assertFalse(set(kwargs.keys()) - set(['account_id', 'user_email', 'xsolla_id', 'payment_sum', 'test']))

        with mock.patch('bank.xsolla.workers.banker.Worker.cmd_handle_invoices') as cmd_handle_invoices:
            invoice = self.fabric.pay(**kwargs)

        self.assertEqual(cmd_handle_invoices.call_count, worker_call_count)

        return invoice


    def test_pay__invoice_exists(self):
        self.assertEqual(InvoicePrototype._db_count(), 0)
        self.create_invoice(worker_call_count=1)
        self.assertEqual(InvoicePrototype._db_count(), 1)
        self.assertTrue(self.pay(worker_call_count=0).pay_result._is_SUCCESS)
        self.assertEqual(InvoicePrototype._db_count(), 1)

    def test_pay__created(self):
        self.assertEqual(InvoicePrototype._db_count(), 0)
        self.assertTrue(self.pay(worker_call_count=1).pay_result._is_SUCCESS)
        self.assertEqual(InvoicePrototype._db_count(), 1)

    def test_create__no_account(self):
        self.assertTrue(self.create_invoice(worker_call_count=0, account_id=None).pay_result._is_USER_NOT_EXISTS)

    def test_create__wrong_sum_format(self):
        self.assertTrue(self.create_invoice(worker_call_count=0, payment_sum='f123.3').pay_result._is_WRONG_SUM_FORMAT)

    def test_create__fraction_in_sum(self):
        self.assertTrue(self.create_invoice(worker_call_count=0, payment_sum='123.3').pay_result._is_FRACTION_IN_SUM)

    def test_create__not_positive_sum(self):
        self.assertTrue(self.create_invoice(worker_call_count=0, payment_sum='-1').pay_result._is_NOT_POSITIVE_SUM)
        self.assertTrue(self.create_invoice(worker_call_count=0, payment_sum='0', xsolla_id='2').pay_result._is_NOT_POSITIVE_SUM)

    def test_create_success(self):
        self.assertEqual(InvoicePrototype._db_count(), 0)

        invoice = self.create_invoice(worker_call_count=1)

        self.assertEqual(InvoicePrototype._db_count(), 1)

        self.assertEqual(invoice.bank_amount, int(self.fabric.payment_sum))
        self.assertEqual(invoice.bank_id, self.fabric.account_id)
        self.assertEqual(invoice.bank_invoice_id, None)
        self.assertTrue(invoice.state._is_CREATED)
        self.assertEqual(invoice.xsolla_id, self.fabric.xsolla_id)
        self.assertEqual(invoice.xsolla_v1, self.fabric.user_email)
        self.assertEqual(invoice.xsolla_v2, self.fabric.v2)
        self.assertEqual(invoice.xsolla_v3, self.fabric.v3)
        self.assertFalse(invoice.test)

        self.assertFalse(invoice.test)
        self.assertTrue(invoice.pay_result._is_SUCCESS)


    def test_create_success__test_not_none__not_test(self):
        self.assertEqual(InvoicePrototype._db_count(), 0)

        invoice = self.create_invoice(worker_call_count=1, test='0')

        self.assertFalse(invoice.test)
        self.assertTrue(invoice.pay_result._is_SUCCESS)


    def test_create_success__test_not_none__test(self):
        self.assertEqual(InvoicePrototype._db_count(), 0)

        invoice = self.create_invoice(worker_call_count=1, test='1')

        self.assertTrue(invoice.test)
        self.assertTrue(invoice.pay_result._is_SUCCESS)


    def test_process__not_in_created_state(self):
        invoice = self.create_invoice(worker_call_count=1)

        for state in INVOICE_STATE._records:
            if state._is_CREATED:
                continue
            invoice.state = state
            invoice.save()

            self.assertRaises(exceptions.WrongInvoiceStateInProcessingError, invoice.process)

            invoice.reload()

            self.assertEqual(invoice.state, state)


    def test_process__test(self):
        self.assertEqual(BankInvoicePrototype._db_count(), 0)

        invoice = self.create_invoice(worker_call_count=1, test='1')
        invoice.process()

        invoice.reload()

        self.assertEqual(BankInvoicePrototype._db_count(), 0)

        self.assertTrue(invoice.state._is_SKIPPED_BECOUSE_TEST)

    def test_process__processed(self):
        self.assertEqual(BankInvoicePrototype._db_count(), 0)

        invoice = self.create_invoice(worker_call_count=1)

        self.assertEqual(invoice.bank_invoice_id, None)

        invoice.process()

        invoice.reload()

        self.assertEqual(BankInvoicePrototype._db_count(), 1)

        self.assertTrue(invoice.state._is_PROCESSED)

        bank_invoice = BankInvoicePrototype._db_get_object(0)

        self.assertEqual(bank_invoice.id, invoice.bank_invoice_id)
        self.assertTrue(bank_invoice.recipient_type._is_GAME_ACCOUNT)
        self.assertEqual(bank_invoice.recipient_id, self.fabric.account_id)
        self.assertTrue(bank_invoice.sender_type._is_XSOLLA)
        self.assertEqual(bank_invoice.sender_id, 0)
        self.assertTrue(bank_invoice.state._is_FORCED)
        self.assertTrue(bank_invoice.currency._is_PREMIUM)
        self.assertTrue(bank_invoice.amount, int(self.fabric.payment_sum))
        self.assertEqual(bank_invoice.operation_uid, 'bank-xsolla')


    def test_process_invoices(self):
        invoice_1 = self.create_invoice(worker_call_count=1, xsolla_id=1)
        invoice_2 = self.create_invoice(worker_call_count=1, xsolla_id=2, test='1')
        invoice_3 = self.create_invoice(worker_call_count=1, xsolla_id=3)
        invoice_4 = self.create_invoice(worker_call_count=1, xsolla_id=4)

        invoice_3.process()

        InvoicePrototype.process_invoices()

        invoice_1.reload()
        invoice_2.reload()
        invoice_3.reload()
        invoice_4.reload()

        self.assertTrue(invoice_1.state._is_PROCESSED)
        self.assertTrue(invoice_2.state._is_SKIPPED_BECOUSE_TEST)
        self.assertTrue(invoice_3.state._is_PROCESSED)
        self.assertTrue(invoice_4.state._is_PROCESSED)

        self.assertTrue(invoice_3.updated_at < invoice_1.updated_at < invoice_2.updated_at < invoice_4.updated_at)
