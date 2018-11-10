
import smart_imports

smart_imports.all()


class BankerTests(utils_testcase.TestCase):

    def setUp(self):
        super(BankerTests, self).setUp()
        self.fabric = helpers.TestInvoiceFabric()
        self.invoice = self.fabric.pay()

        amqp_environment.environment.deinitialize()
        amqp_environment.environment.initialize()

        self.worker = amqp_environment.environment.workers.xsolla_banker

    def test_initialize(self):
        self.worker.initialize()
        self.assertTrue(self.worker.initialized)

    def test_handle_invoices(self):
        with mock.patch('the_tale.finances.xsolla.prototypes.InvoicePrototype.process_invoices') as process_invoices:
            self.worker.handle_invoices()
        self.assertEqual(process_invoices.call_count, 1)

    def test_process_handle_invoices(self):
        with mock.patch('the_tale.finances.xsolla.prototypes.InvoicePrototype.process_invoices') as process_invoices:
            self.worker.process_handle_invoices()
        self.assertEqual(process_invoices.call_count, 1)
