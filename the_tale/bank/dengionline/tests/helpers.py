# coding: utf-8

from bank.relations import ENTITY_TYPE as BANK_ENTITY_TYPE, CURRENCY_TYPE as BANK_CURRENCY_TYPE
from bank.dengionline.relations import CURRENCY_TYPE
from bank.dengionline.prototypes import InvoicePrototype


class TestInvoiceFabric(object):

    def __init__(self):
        self.bank_type = BANK_ENTITY_TYPE.GAME_ACCOUNT
        self.bank_id = 2
        self.bank_currency = BANK_CURRENCY_TYPE.PREMIUM
        self.bank_amount = 13

        self.user_id = 'test@test.com'
        self.comment = u'оплата какой-то покупки'
        self.payment_amount = 10
        self.payment_currency = CURRENCY_TYPE.USD
        self.received_amount = 66
        self.received_currency = CURRENCY_TYPE.RUB
        self.payment_id = 12345
        self.paymode = 22

    def create_invoice(self,
                       bank_type=None,
                       bank_id=None,
                       bank_currency=None,
                       bank_amount=None,
                       user_id=None,
                       comment=None,
                       payment_amount=None,
                       payment_currency=None):
        if bank_type is None:
            bank_type=self.bank_type
        if bank_id is None:
            bank_id=self.bank_id
        if bank_currency is None:
            bank_currency=self.bank_currency
        if bank_amount is None:
            bank_amount=self.bank_amount
        if user_id is None:
            user_id=self.user_id
        if comment is None:
            comment=self.comment
        if payment_amount is None:
            payment_amount=self.payment_amount
        if payment_currency is None:
            payment_currency=self.payment_currency
        return InvoicePrototype.create(bank_type=bank_type,
                                       bank_id=bank_id,
                                       bank_currency=bank_currency,
                                       bank_amount=bank_amount,
                                       user_id=user_id,
                                       comment=comment,
                                       payment_amount=payment_amount,
                                       payment_currency=payment_currency)
