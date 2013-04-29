# coding: utf-8
import time
import Queue
import datetime

from django.utils.log import getLogger

from dext.settings import settings

from common.amqp_queues import connection, BaseWorker

from bank.prototypes import InvoicePrototype
from bank.conf import bank_settings


class BankException(Exception): pass


class Worker(BaseWorker):

    def __init__(self, messages_queue, stop_queue):
        super(Worker, self).__init__(logger=getLogger('the-tale.workers.bank_bank'), command_queue=messages_queue)
        self.stop_queue = connection.SimpleQueue(stop_queue)

    def clean_queues(self):
        super(Worker, self).clean_queues()
        self.stop_queue.queue.purge()

    def initialize(self):
        self.initialized = True
        self.next_invoice_process_time = datetime.datetime.now()
        self.logger.info('BANK INITIALIZED')

    def run(self):

        while not self.exception_raised and not self.stop_required:
            try:
                cmd = self.command_queue.get_nowait()
                cmd.ack()
                self.process_cmd(cmd.payload)
            except Queue.Empty:
                if self.next_invoice_process_time < datetime.datetime.now():
                    if not self.freeze_invoice(InvoicePrototype.get_unprocessed_invoice()):
                        self.next_invoice_process_time = datetime.datetime.now() + datetime.timedelta(seconds=bank_settings.BANK_DELAY)
                time.sleep(0.1)

    def freeze_invoice(self, invoice):

        settings.refresh()

        if invoice is None:
            return False

        if (not bank_settings.ENABLE_BANK or
            settings.get(bank_settings.SETTINGS_ALLOWED_KEY) is None):
            self.logger.info('postpone invoice %s' % invoice.id)
            return True

        self.logger.info('process invoice %s' % invoice.uid)

        invoice.freeze()

        if invoice.state._is_PROCESSED:
            self.logger.info('invoice %s status %s' % (invoice.id, invoice.state))
        else:
            self.logger.error('invoice %s status %s ' % (invoice.id, invoice.state))

        return True

    def cmd_freeze_invoice(self):
        return self.send_cmd('process_invoice', {})

    def process_freeze_invoice(self, message_id):
        self._process_invoice(InvoicePrototype.get_unprocessed_invoice())

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.initialized = False
        self.stop_required = True
        self.stop_queue.put({'code': 'stopped', 'worker': 'bank'}, serializer='json', compression=None)
        self.logger.info('BANK STOPPED')
