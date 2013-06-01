# coding: utf-8

import mock

from common.utils import testcase

from bank.workers.environment import workers_environment as bank_workers_environment

from bank.dengionline.tests.helpers import TestInvoiceFabric


class BankerTests(testcase.TestCase):

    def setUp(self):
        super(BankerTests, self).setUp()
        self.fabric = TestInvoiceFabric()
        self.invoice = self.fabric.create_invoice()

        bank_workers_environment.deinitialize()
        bank_workers_environment.initialize()

        self.worker = bank_workers_environment.dengionline_banker

    def test_initialize(self):
        self.worker.initialize()
        self.assertTrue(self.worker.initialized)

    def test_handle_confirmed_invoices(self):
        with mock.patch('bank.dengionline.prototypes.InvoicePrototype.process_confirmed_invoices') as process_confirmed_invoices:
            self.worker.handle_confirmed_invoices()
        self.assertEqual(process_confirmed_invoices.call_count, 1)

    def test_process_handle_confirmations(self):
        with mock.patch('bank.dengionline.prototypes.InvoicePrototype.process_confirmed_invoices') as process_confirmed_invoices:
            self.worker.process_handle_confirmations()
        self.assertEqual(process_confirmed_invoices.call_count, 1)
