# coding: utf-8
import Queue

from dext.settings import settings

from the_tale.common.utils.workers import BaseWorker

from the_tale.bank.xsolla.prototypes import InvoicePrototype

class Worker(BaseWorker):

    def clean_queues(self):
        super(Worker, self).clean_queues()
        self.stop_queue.queue.purge()

    def initialize(self):
        self.initialized = True
        self.logger.info('XSOLLA BANKER INITIALIZED')

    def run(self):

        while not self.exception_raised and not self.stop_required:
            try:
                cmd = self.command_queue.get(block=True, timeout=60)
                # cmd.ack()

                settings.refresh()
                self.process_cmd(cmd.payload)
            except Queue.Empty:
                settings.refresh()
                self.run_commands()

    def run_commands(self):
        self.handle_invoices()

    def handle_invoices(self):
        InvoicePrototype.process_invoices()

    def cmd_handle_invoices(self):
        return self.send_cmd('handle_invoices')

    def process_handle_invoices(self):
        self.handle_invoices()

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.initialized = False
        self.stop_required = True
        self.stop_queue.put({'code': 'stopped', 'worker': 'xsolla_banker'}, serializer='json', compression=None)
        self.logger.info('XSOLLA BANKER STOPPED')
