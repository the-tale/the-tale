# coding: utf-8
import mock

from dext.settings import settings

from the_tale.amqp_environment import environment

from the_tale.common.utils import testcase

from the_tale.finances.bank.tests.helpers import BankTestsMixin

from the_tale.finances.bank.conf import bank_settings


class BankTests(testcase.TestCase, BankTestsMixin):

    def setUp(self):
        super(BankTests, self).setUp()

        environment.deinitialize()
        environment.initialize()

        settings[bank_settings.SETTINGS_ALLOWED_KEY] = 'allowed'

        self.worker = environment.workers.bank_processor

    def test_initialize__reset_invoices(self):
        with mock.patch('the_tale.finances.bank.prototypes.InvoicePrototype.reset_all') as reset_all:
            self.worker.initialize()

        self.assertEqual(reset_all.call_count, 1)

    @mock.patch('the_tale.finances.bank.conf.bank_settings.ENABLE_BANK', False)
    @mock.patch('the_tale.finances.bank.conf.bank_settings.BANK_PROCESSOR_SLEEP_TIME', 0)
    def test_run__turn_off_by_configs(self):
        invoice = self.create_invoice()
        self.worker.process_init_invoice()
        invoice.reload()
        self.assertTrue(invoice.state.is_REQUESTED)

    @mock.patch('the_tale.finances.bank.conf.bank_settings.BANK_PROCESSOR_SLEEP_TIME', 0)
    def test_init_invoice__turn_off_by_settings(self):
        del settings[bank_settings.SETTINGS_ALLOWED_KEY]
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
