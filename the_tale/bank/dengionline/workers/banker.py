# coding: utf-8
import Queue

from django.utils.log import getLogger

from dext.settings import settings

from common.amqp_queues import connection, BaseWorker

from bank.dengionline.prototypes import InvoicePrototype

class Worker(BaseWorker):

    logger = getLogger('the-tale.workers.bank_dengionline_banker')
    name = 'dengionline banker'
    command_name = 'dengionline_banker'

    def __init__(self, messages_queue, stop_queue):
        super(Worker, self).__init__(command_queue=messages_queue)
        self.stop_queue = connection.SimpleQueue(stop_queue)

    def clean_queues(self):
        super(Worker, self).clean_queues()
        self.stop_queue.queue.purge()

    def initialize(self):
        self.initialized = True
        self.logger.info('DENGIONLINE BANKER INITIALIZED')

    def run(self):

        while not self.exception_raised and not self.stop_required:
            try:
                cmd = self.command_queue.get(block=True, timeout=60)
                cmd.ack()

                settings.refresh()
                self.process_cmd(cmd.payload)
            except Queue.Empty:
                settings.refresh()
                self.run_commands()

    def run_commands(self):
        InvoicePrototype.discard_old_invoices()
        self.handle_confirmed_invoices()

    def handle_confirmed_invoices(self):
        InvoicePrototype.process_confirmed_invoices()

    def cmd_handle_confirmations(self):
        return self.send_cmd('handle_confirmations')

    def process_handle_confirmations(self):
        self.handle_confirmed_invoices()

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.initialized = False
        self.stop_required = True
        self.stop_queue.put({'code': 'stopped', 'worker': 'dengionline_banker'}, serializer='json', compression=None)
        self.logger.info('DENGIONLINE BANKER STOPPED')
