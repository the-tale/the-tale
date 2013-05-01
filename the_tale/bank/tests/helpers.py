# coding: utf-8

from bank.prototypes import InvoicePrototype
from bank.relations import ENTITY_TYPE, CURRENCY_TYPE


class BankTestsMixin(object):

    def create_invoice(self,
                       recipient_type=ENTITY_TYPE.GAME_ACCOUNT,
                       recipient_id=3,
                       sender_type=ENTITY_TYPE.GAME_LOGIC,
                       sender_id=8,
                       currency=CURRENCY_TYPE.PREMIUM,
                       amount = 317,
                       state=None):
        invoice = InvoicePrototype.create(recipient_type=recipient_type,
                                          recipient_id=recipient_id,
                                          sender_type=sender_type,
                                          sender_id=sender_id,
                                          currency=currency,
                                          amount=amount)
        if state is not None:
            invoice.state = state
            invoice.save()

        return invoice
