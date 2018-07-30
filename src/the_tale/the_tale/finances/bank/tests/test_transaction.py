
import smart_imports

smart_imports.all()


class TransactionTests(utils_testcase.TestCase, helpers.BankTestsMixin):

    def setUp(self):
        super(TransactionTests, self).setUp()

    def create_transaction(self):
        return transaction.Transaction.create(recipient_type=relations.ENTITY_TYPE.GAME_ACCOUNT,
                                              recipient_id=2,
                                              sender_type=relations.ENTITY_TYPE.GAME_LOGIC,
                                              sender_id=3,
                                              currency=relations.CURRENCY_TYPE.PREMIUM,
                                              amount=113,
                                              description_for_sender='transaction description for sender',
                                              description_for_recipient='transaction description for recipient',
                                              operation_uid='transaction-operation-uid')

    def test_create(self):
        with mock.patch('the_tale.finances.bank.workers.bank_processor.Worker.cmd_init_invoice') as cmd_init_invoice:
            transaction = self.create_transaction()
        self.assertEqual(cmd_init_invoice.call_count, 1)

        self.assertEqual(prototypes.InvoicePrototype._model_class.objects.all().count(), 1)

        invoice = prototypes.InvoicePrototype._db_get_object(0)

        self.assertEqual(transaction.invoice_id, prototypes.InvoicePrototype._db_get_object(0).id)

        self.assertTrue(invoice.state.is_REQUESTED)
        self.assertEqual(invoice.recipient_type, relations.ENTITY_TYPE.GAME_ACCOUNT)
        self.assertEqual(invoice.recipient_id, 2)
        self.assertEqual(invoice.sender_type, relations.ENTITY_TYPE.GAME_LOGIC)
        self.assertEqual(invoice.sender_id, 3)
        self.assertEqual(invoice.currency, relations.CURRENCY_TYPE.PREMIUM)
        self.assertEqual(invoice.amount, 113)
        self.assertEqual(invoice.description_for_sender, 'transaction description for sender')
        self.assertEqual(invoice.description_for_recipient, 'transaction description for recipient')
        self.assertEqual(invoice.operation_uid, 'transaction-operation-uid')

    def test_confirm(self):
        transaction = self.create_transaction()
        with mock.patch('the_tale.finances.bank.workers.bank_processor.Worker.cmd_confirm_invoice') as cmd_confirm_invoice:
            transaction.confirm()
        self.assertEqual(cmd_confirm_invoice.call_count, 1)

    def test_cancel(self):
        transaction = self.create_transaction()
        with mock.patch('the_tale.finances.bank.workers.bank_processor.Worker.cmd_cancel_invoice') as cmd_count_invoice:
            transaction.cancel()
        self.assertEqual(cmd_count_invoice.call_count, 1)
