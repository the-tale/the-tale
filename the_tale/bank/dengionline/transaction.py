# coding: utf-8


from bank.dengionline.prototypes import InvoicePrototype


class Transaction(object):

    def __init__(self, invoice_id):
        self.invoice_id = invoice_id

    def serialize(self):
        return {'invoice_id': self.invoice_id}

    @classmethod
    def deserialize(cls, data):
        return cls(**data)

    @classmethod
    def create(cls, bank_type, bank_id, bank_currency, bank_amount, email, comment, payment_amount, payment_currency):
        invoice = InvoicePrototype.create(bank_type=bank_type,
                                          bank_id=bank_id,
                                          bank_currency=bank_currency,
                                          bank_amount=bank_amount,
                                          user_id=email,
                                          comment=comment,
                                          payment_amount=payment_amount,
                                          payment_currency=payment_currency)

        return cls(invoice_id=invoice.id)

    def get_simple_payment_url(self):
        return InvoicePrototype.get_by_id(self.invoice_id).simple_payment_url
