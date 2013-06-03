# coding: utf-8

from decimal import Decimal

from datetime import datetime

from bank.dengionline.prototypes import InvoicePrototype
from bank.dengionline.relations import INVOICE_STATE
from bank.dengionline.conf import dengionline_settings
from bank.dengionline import exceptions

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

        requested_count = InvoicePrototype._db_filter(bank_type=bank_type,
                                                      bank_id=bank_id,
                                                      bank_currency=bank_currency,
                                                      state=INVOICE_STATE.REQUESTED,
                                                      created_at__gt=datetime.now()-dengionline_settings.CREATION_TIME_LIMIT).count()

        if requested_count >= dengionline_settings.CREATION_NUMBER_LIMIT:
            raise exceptions.CreationLimitError(account_id=bank_id)

        invoice = InvoicePrototype.create(bank_type=bank_type,
                                          bank_id=bank_id,
                                          bank_currency=bank_currency,
                                          bank_amount=bank_amount,
                                          user_id=email,
                                          comment=comment,
                                          payment_amount=Decimal(payment_amount),
                                          payment_currency=payment_currency)

        return cls(invoice_id=invoice.id)

    def get_simple_payment_url(self):
        return InvoicePrototype.get_by_id(self.invoice_id).simple_payment_url
