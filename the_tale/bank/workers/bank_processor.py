# coding: utf-8
import time
import datetime
import Queue

from django.utils.log import getLogger

from dext.settings import settings

from common.amqp_queues import connection, BaseWorker

from bank.prototypes import InvoicePrototype
from bank.conf import bank_settings


class BankException(Exception): pass


class Worker(BaseWorker):

    logger = getLogger('the-tale.workers.bank_bank_processor')
    name = 'bank processor'
    command_name = 'bank_bank_processor'

    def __init__(self, messages_queue, stop_queue):
        super(Worker, self).__init__(command_queue=messages_queue)
        self.stop_queue = connection.SimpleQueue(stop_queue)

    def clean_queues(self):
        super(Worker, self).clean_queues()
        self.stop_queue.queue.purge()

    def initialize(self):
        self.initialized = True
        self.next_invoice_process_time = datetime.datetime.now()

        InvoicePrototype.reset_all()

        self.logger.info('BANK PROCESSOR INITIALIZED')

    def run(self):
        while not self.exception_raised and not self.stop_required:
            try:
                settings.refresh()

                cmd = self.command_queue.get_nowait()
                cmd.ack()

                self.process_cmd(cmd.payload)
            except Queue.Empty:
                self.process_freeze_invoice(self)
                time.sleep(0.1)


    def cmd_freeze_invoice(self):
        return self.send_cmd('freeze_invoice', {})

    def process_freeze_invoice(self):

        invoice = InvoicePrototype.get_unprocessed_invoice()

        if invoice is None:
            return

        if (not bank_settings.ENABLE_BANK or
            settings.get(bank_settings.SETTINGS_ALLOWED_KEY) is None):
            self.logger.info('postpone invoice %d' % invoice.id)
            return

        self.logger.info('process invoice %s' % invoice.id)

        invoice.freeze()

        self.logger.info('invoice %s status %s' % (invoice.id, invoice.state))


    def cmd_confirm_invoice(self, invoice_id):
        return self.send_cmd('confirm_invoice', {'invoice_id': invoice_id})

    def process_confirm_invoice(self, invoice_id):
        InvoicePrototype.get_by_id(invoice_id).confirm()

    def cmd_cancel_invoice(self, invoice_id):
        return self.send_cmd('cancel_invoice', {'invoice_id': invoice_id})

    def process_cancel_invoice(self, invoice_id):
        InvoicePrototype.get_by_id(invoice_id).cancel()

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.initialized = False
        self.stop_required = True
        self.stop_queue.put({'code': 'stopped', 'worker': 'bank_processor'}, serializer='json', compression=None)
        self.logger.info('BANK PROCESSOR STOPPED')
