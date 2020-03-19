
import smart_imports

smart_imports.all()


class BankTests(utils_testcase.TestCase, helpers.BankTestsMixin):

    def setUp(self):
        super(BankTests, self).setUp()

        amqp_environment.environment.deinitialize()
        amqp_environment.environment.initialize()

        global_settings[conf.settings.SETTINGS_ALLOWED_KEY] = 'allowed'

        self.worker = amqp_environment.environment.workers.bank_processor

    def test_initialize__reset_invoices(self):
        with mock.patch('the_tale.finances.bank.prototypes.InvoicePrototype.reset_all') as reset_all:
            self.worker.initialize()

        self.assertEqual(reset_all.call_count, 1)

    @mock.patch('the_tale.finances.bank.conf.settings.ENABLE_BANK', False)
    @mock.patch('the_tale.finances.bank.conf.settings.BANK_PROCESSOR_SLEEP_TIME', 0)
    def test_run__turn_off_by_configs(self):
        invoice = self.create_invoice()
        self.worker.process_init_invoice()
        invoice.reload()
        self.assertTrue(invoice.state.is_REQUESTED)

    @mock.patch('the_tale.finances.bank.conf.settings.BANK_PROCESSOR_SLEEP_TIME', 0)
    def test_init_invoice__turn_off_by_settings(self):
        del global_settings[conf.settings.SETTINGS_ALLOWED_KEY]
        invoice = self.create_invoice()
        self.worker.process_init_invoice()
        invoice.reload()
        self.assertTrue(invoice.state.is_REQUESTED)

    def test_init_invoice__no_invoice(self):
        self.worker.process_init_invoice()

    def test_init_invoice(self):
        invoice = self.create_invoice()
        self.worker.process_init_invoice()
        invoice.reload()
        self.assertTrue(invoice.state.is_FROZEN)

    def test_init_invoice__forced(self):
        invoice = self.create_invoice(force=True)
        self.worker.process_init_invoice()
        invoice.reload()
        self.assertTrue(invoice.state.is_CONFIRMED)

    def test_confirm_invoice(self):
        invoice = self.create_invoice()
        self.worker.process_init_invoice()
        self.worker.process_confirm_invoice(invoice.id)
        invoice.reload()
        self.assertTrue(invoice.state.is_CONFIRMED)

    def test_cancel_invoice(self):
        invoice = self.create_invoice()
        self.worker.process_init_invoice()
        self.worker.process_cancel_invoice(invoice.id)
        invoice.reload()
        self.assertTrue(invoice.state.is_CANCELED)
