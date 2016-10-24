# coding: utf-8

from the_tale.common.utils.workers import BaseWorker

from the_tale.finances.xsolla.prototypes import InvoicePrototype

class Worker(BaseWorker):
    GET_CMD_TIMEOUT = 10

    def clean_queues(self):
        super(Worker, self).clean_queues()
        self.stop_queue.queue.purge()

    def initialize(self):
        self.initialized = True
        self.logger.info('XSOLLA BANKER INITIALIZED')

    def process_no_cmd(self):
        self.handle_invoices()

    def handle_invoices(self):
        InvoicePrototype.process_invoices()

    def cmd_handle_invoices(self):
        return self.send_cmd('handle_invoices')

    def process_handle_invoices(self):
        self.handle_invoices()
