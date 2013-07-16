# coding: utf-8

from decimal import Decimal

from django.db import IntegrityError

from common.utils.prototypes import BasePrototype

from bank import logic as bank_logic

from bank.xsolla.models import Invoice
from bank.xsolla.relations import PAY_RESULT, INVOICE_STATE
from bank.xsolla import exceptions


class InvoicePrototype(BasePrototype):
    _model_class = Invoice
    _readonly = ('id',
                 'updated_at',
                 'bank_id',
                 'bank_amount',
                 'bank_invoice_id',
                 'xsolla_id',
                 'xsolla_v1',
                 'xsolla_v2',
                 'xsolla_v3',
                 'test',
                 'comment',
                 'pay_result')
    _bidirectional = ('state',)
    _get_by = ('id', 'xsolla_id')


    @classmethod
    def pay(cls, v1, v2, v3, xsolla_id, payment_sum, test):

        invoice = cls.get_by_xsolla_id(xsolla_id)

        if invoice is not None:
            return invoice

        try:
            return cls.create(v1=v1, v2=v2, v3=v3, xsolla_id=xsolla_id, payment_sum=payment_sum, test=test)
        except IntegrityError:
            return cls.get_by_xsolla_id(xsolla_id)

    @classmethod
    def create(cls, v1, v2, v3, xsolla_id, payment_sum, test):
        from bank.workers.environment import workers_environment

        user_email = v1

        results = []

        test = test not in (None, '0')

        account_id = bank_logic.get_account_id(email=user_email)

        if account_id is None:
            account_id = -1
            results.append(PAY_RESULT.USER_NOT_EXISTS)

        try:
            real_sum = Decimal(payment_sum)
        except:
            real_sum = Decimal('0')
            results.append(PAY_RESULT.WRONG_SUM_FORMAT)

        if real_sum % 1 != 0:
            real_sum //= 1
            results.append(PAY_RESULT.FRACTION_IN_SUM)

        if real_sum <= 0:
            results.append(PAY_RESULT.NOT_POSITIVE_SUM)

        results.append(PAY_RESULT.SUCCESS) #success result MUST be appended at the end of every checking

        pay_result = results[0] # get first result

        model = cls._model_class.objects.create(state=pay_result.invoice_state,
                                                bank_id=account_id,
                                                bank_amount=real_sum,
                                                bank_invoice=None,

                                                xsolla_id=xsolla_id,
                                                xsolla_v1=v1,
                                                xsolla_v2=v2,
                                                xsolla_v3=v3,

                                                pay_result=pay_result,

                                                test=test)

        prototype = cls(model=model)

        if prototype.state._is_CREATED:
            workers_environment.xsolla_banker.cmd_handle_invoices()

        return prototype

    def process(self):
        from bank.transaction import Transaction
        from bank.relations import ENTITY_TYPE, CURRENCY_TYPE

        if not self.state._is_CREATED:
            raise exceptions.WrongInvoiceStateInProcessingError(invoice_id=self.id, state=self.state)

        if self.test:
            self.state = INVOICE_STATE.SKIPPED_BECOUSE_TEST
            self.save()
            return

        transaction = Transaction.create(recipient_type=ENTITY_TYPE.GAME_ACCOUNT,
                                         recipient_id=self.bank_id,
                                         sender_type=ENTITY_TYPE.XSOLLA,
                                         sender_id=0,
                                         currency=CURRENCY_TYPE.PREMIUM,
                                         amount=self.bank_amount,
                                         description=u'Покупка печенек (через Xsolla)',
                                         operation_uid='bank-xsolla',
                                         force=True)

        self._model.bank_invoice_id = transaction.invoice_id
        self.state = INVOICE_STATE.PROCESSED
        self.save()


    @classmethod
    def process_invoices(cls):
        for model in cls._model_class.objects.filter(state=INVOICE_STATE.CREATED).order_by('created_at'):
            invoice = cls(model=model)
            invoice.process()

    def save(self):
        self._model.save()
