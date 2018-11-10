
import smart_imports

smart_imports.all()


class Transaction(object):

    def __init__(self, invoice_id):
        self.invoice_id = invoice_id

    def serialize(self):
        return {'invoice_id': self.invoice_id}

    @classmethod
    def deserialize(cls, data):
        return cls(**data)

    @classmethod
    def create(cls, recipient_type, recipient_id, sender_type, sender_id, currency, amount, description_for_sender, description_for_recipient, operation_uid, force=False):
        invoice = prototypes.InvoicePrototype.create(recipient_type=recipient_type,
                                                     recipient_id=recipient_id,
                                                     sender_type=sender_type,
                                                     sender_id=sender_id,
                                                     currency=currency,
                                                     amount=amount,
                                                     description_for_sender=description_for_sender,
                                                     description_for_recipient=description_for_recipient,
                                                     operation_uid=operation_uid,
                                                     force=force)

        amqp_environment.environment.workers.bank_processor.cmd_init_invoice()

        return cls(invoice_id=invoice.id)

    def get_invoice(self):
        return prototypes.InvoicePrototype.get_by_id(self.invoice_id)

    def get_invoice_state(self):
        return prototypes.InvoicePrototype.get_by_id(self.invoice_id).state

    def confirm(self):
        amqp_environment.environment.workers.bank_processor.cmd_confirm_invoice(self.invoice_id)

    def cancel(self):
        amqp_environment.environment.workers.bank_processor.cmd_cancel_invoice(self.invoice_id)
