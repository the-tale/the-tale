# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.bank.tests.helpers import BankTestsMixin

from the_tale.bank.prototypes import InvoicePrototype
from the_tale.bank.relations import ENTITY_TYPE, CURRENCY_TYPE
from the_tale.bank.transaction import Transaction


class TransactionTests(testcase.TestCase, BankTestsMixin):

    def setUp(self):
        super(TransactionTests, self).setUp()

    def create_transaction(self):
        return Transaction.create(recipient_type=ENTITY_TYPE.GAME_ACCOUNT,
                                  recipient_id=2,
                                  sender_type=ENTITY_TYPE.GAME_LOGIC,
                                  sender_id=3,
                                  currency=CURRENCY_TYPE.PREMIUM,
                                  amount=113,
                                  description='transaction description',
                                  operation_uid='transaction-operation-uid')


    def test_create(self):
        with mock.patch('the_tale.bank.workers.bank_processor.Worker.cmd_init_invoice') as cmd_init_invoice:
            transaction = self.create_transaction()
        self.assertEqual(cmd_init_invoice.call_count, 1)

        self.assertEqual(InvoicePrototype._model_class.objects.all().count(), 1)

        invoice = InvoicePrototype._db_get_object(0)

        self.assertEqual(transaction.invoice_id, InvoicePrototype._db_get_object(0).id)

        self.assertTrue(invoice.state._is_REQUESTED)
        self.assertEqual(invoice.recipient_type, ENTITY_TYPE.GAME_ACCOUNT)
        self.assertEqual(invoice.recipient_id, 2)
        self.assertEqual(invoice.sender_type, ENTITY_TYPE.GAME_LOGIC)
        self.assertEqual(invoice.sender_id, 3)
        self.assertEqual(invoice.currency, CURRENCY_TYPE.PREMIUM)
        self.assertEqual(invoice.amount, 113)
        self.assertEqual(invoice.description, 'transaction description')
        self.assertEqual(invoice.operation_uid, 'transaction-operation-uid')

    def test_confirm(self):
        transaction = self.create_transaction()
        with mock.patch('the_tale.bank.workers.bank_processor.Worker.cmd_confirm_invoice') as cmd_confirm_invoice:
            transaction.confirm()
        self.assertEqual(cmd_confirm_invoice.call_count, 1)

    def test_cancel(self):
        transaction = self.create_transaction()
        with mock.patch('the_tale.bank.workers.bank_processor.Worker.cmd_cancel_invoice') as cmd_count_invoice:
            transaction.cancel()
        self.assertEqual(cmd_count_invoice.call_count, 1)
