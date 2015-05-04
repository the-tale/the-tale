# coding: utf-8

import mock

from the_tale.amqp_environment import environment

from the_tale.common.utils import testcase

from the_tale.bank.xsolla.tests.helpers import TestInvoiceFabric


class BankerTests(testcase.TestCase):

    def setUp(self):
        super(BankerTests, self).setUp()
        self.fabric = TestInvoiceFabric()
        self.invoice = self.fabric.pay()

        environment.deinitialize()
        environment.initialize()

        self.worker = environment.workers.xsolla_banker

    def test_initialize(self):
        self.worker.initialize()
        self.assertTrue(self.worker.initialized)

    def test_handle_invoices(self):
        with mock.patch('the_tale.bank.xsolla.prototypes.InvoicePrototype.process_invoices') as process_invoices:
            self.worker.handle_invoices()
        self.assertEqual(process_invoices.call_count, 1)

    def test_process_handle_invoices(self):
        with mock.patch('the_tale.bank.xsolla.prototypes.InvoicePrototype.process_invoices') as process_invoices:
            self.worker.process_handle_invoices()
        self.assertEqual(process_invoices.call_count, 1)
