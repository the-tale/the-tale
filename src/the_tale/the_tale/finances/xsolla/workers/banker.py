
import smart_imports

smart_imports.all()


class Worker(utils_workers.BaseWorker):
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
        prototypes.InvoicePrototype.process_invoices()

    def cmd_handle_invoices(self):
        return self.send_cmd('handle_invoices')

    def process_handle_invoices(self):
        self.handle_invoices()
