# coding: utf-8

import mock

from common.utils import testcase

from bank.workers.environment import workers_environment as bank_workers_environment

from bank.xsolla.tests.helpers import TestInvoiceFabric


class BankerTests(testcase.TestCase):

    def setUp(self):
        super(BankerTests, self).setUp()
        self.fabric = TestInvoiceFabric()
        self.invoice = self.fabric.pay()

        bank_workers_environment.deinitialize()
        bank_workers_environment.initialize()

        self.worker = bank_workers_environment.xsolla_banker

    def test_initialize(self):
        self.worker.initialize()
        self.assertTrue(self.worker.initialized)

    def test_handle_invoices(self):
        with mock.patch('bank.xsolla.prototypes.InvoicePrototype.process_invoices') as process_invoices:
            self.worker.handle_invoices()
        self.assertEqual(process_invoices.call_count, 1)

    def test_process_handle_invoices(self):
        with mock.patch('bank.xsolla.prototypes.InvoicePrototype.process_invoices') as process_invoices:
            self.worker.process_handle_invoices()
        self.assertEqual(process_invoices.call_count, 1)
