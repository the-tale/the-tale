# coding: utf-8


from bank.prototypes import InvoicePrototype
from bank.workers.environment import workers_environment as bank_workers_environment


class Transaction(object):

    def __init__(self, invoice_id):
        self.invoice_id = invoice_id

    def serialize(self):
        return {'invoice_id': self.invoice_id}

    @classmethod
    def deserialize(cls, data):
        return cls(**data)

    @classmethod
    def create(cls, recipient_type, recipient_id, sender_type, sender_id, currency, amount, description, operation_uid, force=False):
        invoice = InvoicePrototype.create(recipient_type=recipient_type,
                                          recipient_id=recipient_id,
                                          sender_type=sender_type,
                                          sender_id=sender_id,
                                          currency=currency,
                                          amount=amount,
                                          description=description,
                                          operation_uid=operation_uid,
                                          force=force)

        bank_workers_environment.bank_processor.cmd_init_invoice()

        return cls(invoice_id=invoice.id)

    def get_invoice(self):
        return InvoicePrototype.get_by_id(self.invoice_id)

    def get_invoice_state(self):
        return InvoicePrototype.get_by_id(self.invoice_id).state

    def confirm(self):
        bank_workers_environment.bank_processor.cmd_confirm_invoice(self.invoice_id)

    def cancel(self):
        bank_workers_environment.bank_processor.cmd_cancel_invoice(self.invoice_id)
