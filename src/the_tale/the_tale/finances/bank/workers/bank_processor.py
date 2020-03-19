
import smart_imports

smart_imports.all()


class BankException(Exception):
    pass


class Worker(utils_workers.BaseWorker):
    GET_CMD_TIMEOUT = 0.25

    def clean_queues(self):
        super(Worker, self).clean_queues()
        self.stop_queue.queue.purge()

    def initialize(self):
        self.initialized = True
        self.next_invoice_process_time = datetime.datetime.now()

        prototypes.InvoicePrototype.reset_all()

        self.logger.info('BANK PROCESSOR INITIALIZED')

    def process_no_cmd(self):
        self.process_init_invoice()
        self.check_frozen_expired_invoices()

    def check_frozen_expired_invoices(self):

        if time.time() - float(global_settings.get(conf.settings.SETTINGS_LAST_FROZEN_EXPIRED_CHECK_KEY, 0)) < conf.settings.FROZEN_INVOICE_EXPIRED_CHECK_TIMEOUT:
            return

        global_settings[conf.settings.SETTINGS_LAST_FROZEN_EXPIRED_CHECK_KEY] = str(time.time())

        if not prototypes.InvoicePrototype.check_frozen_expired_invoices():
            return

        self.logger.error('We have some expired frozen invoices. Please, check them and remove or find error.')

    def cmd_init_invoice(self):
        return self.send_cmd('init_invoice', {})

    def process_init_invoice(self):

        invoice = prototypes.InvoicePrototype.get_unprocessed_invoice()

        if invoice is None:
            return

        if (not conf.settings.ENABLE_BANK or
                global_settings.get(conf.settings.SETTINGS_ALLOWED_KEY) is None):
            self.logger.info('postpone invoice %d' % invoice.id)
            return

        self.logger.info('process invoice %s' % invoice.id)

        if invoice.state.is_REQUESTED:
            invoice.freeze()
        elif invoice.state.is_FORCED:
            invoice.force()
        else:
            raise BankException('unknown invoice %d state %s' % (invoice.id, invoice.state))

        self.logger.info('invoice %s status %s' % (invoice.id, invoice.state))

    def cmd_confirm_invoice(self, invoice_id):
        return self.send_cmd('confirm_invoice', {'invoice_id': invoice_id})

    def process_confirm_invoice(self, invoice_id):
        invoice = prototypes.InvoicePrototype.get_by_id(invoice_id)

        if invoice:
            invoice.confirm()

    def cmd_cancel_invoice(self, invoice_id):
        return self.send_cmd('cancel_invoice', {'invoice_id': invoice_id})

    def process_cancel_invoice(self, invoice_id):
        invoice = prototypes.InvoicePrototype.get_by_id(invoice_id)

        if invoice:
            invoice.cancel()
