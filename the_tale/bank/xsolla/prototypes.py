# coding: utf-8
import time
import datetime

from decimal import Decimal

from django.db import IntegrityError

from the_tale.amqp_environment import environment

from the_tale.common.utils.prototypes import BasePrototype

from the_tale.bank import logic as bank_logic

from the_tale.bank.xsolla.models import Invoice
from the_tale.bank.xsolla.relations import PAY_RESULT, INVOICE_STATE
from the_tale.bank.xsolla import exceptions


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
                 'date',
                 'comment',
                 'pay_result',
                 'request_url')
    _bidirectional = ('state',)
    _get_by = ('id',)

    @classmethod
    def parse_test(cls, test):
        return test not in (None, '0')

    @classmethod
    def get_by_xsolla_id(cls, xsolla_id, test):
        try:
            return cls(model=cls._model_class.objects.get(xsolla_id=xsolla_id, test=test))
        except cls._model_class.DoesNotExist:
            return None


    @classmethod
    def pay(cls, v1, v2, v3, xsolla_id, payment_sum, test, date, request_url):

        invoice = cls.get_by_xsolla_id(xsolla_id=xsolla_id, test=cls.parse_test(test))

        if invoice is not None:
            return invoice

        try:
            return cls.create(v1=v1, v2=v2, v3=v3, xsolla_id=xsolla_id, payment_sum=payment_sum, test=test, date=date, request_url=request_url)
        except IntegrityError:
            return cls.get_by_xsolla_id(xsolla_id)

    @classmethod
    def create(cls, v1, v2, v3, xsolla_id, payment_sum, test, date, request_url):
        user_email = v1

        results = []

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

        if date is not None:
            try:
                date = datetime.datetime.fromtimestamp(time.mktime(time.strptime(date, '%Y-%m-%d %H:%M:%S')))
            except ValueError:
                date = None
                results.append(PAY_RESULT.WRONG_DATE_FORMAT)

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

                                                test=cls.parse_test(test),
                                                date=date,
                                                request_url=request_url[:cls._model_class.REQUEST_URL_LENGTH])

        prototype = cls(model=model)

        if prototype.state.is_CREATED:
            environment.workers.xsolla_banker.cmd_handle_invoices()

        return prototype

    def process(self):
        from the_tale.bank.transaction import Transaction
        from the_tale.bank.relations import ENTITY_TYPE, CURRENCY_TYPE

        if not self.state.is_CREATED:
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
                                         description_for_sender=u'Покупка печенек (через Xsolla)',
                                         description_for_recipient=u'Покупка печенек (через Xsolla)',
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
