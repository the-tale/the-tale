# coding: utf-8
import md5
import urllib

import rels

from datetime import datetime
from decimal import Decimal

from dext.utils.decorators import nested_commit_on_success

from common.utils.prototypes import BasePrototype

from bank.dengionline.models import Invoice
from bank.dengionline.conf import dengionline_settings
from bank.dengionline.relations import INVOICE_STATE, CHECK_USER_RESULT, CONFIRM_PAYMENT_RESULT, CURRENCY_TYPE
from bank.dengionline import exceptions


class InvoicePrototype(BasePrototype):
    _model_class = Invoice
    _readonly = ('id',
                 'bank_type',
                 'bank_id',
                 'bank_currency',
                 'bank_amount',
                 'user_id',
                 'comment',
                 'payment_amount',
                 'payment_currency',
                 'received_amount',
                 'received_currency',
                 'paymode',
                 'state')
    _bidirectional = ()
    _get_by = ('id', 'payment_id')

    @property
    def payment_id(self): return int(self._model.payment_id) if self._model.payment_id is not None else None

    @classmethod
    def check_types(cls, **kwargs):
        for key, values in kwargs.items():
            value, expected_type = values
            if not isinstance(value, expected_type):
                raise exceptions.WrongValueTypeError(value_name=key, type=value.__class__)

    @classmethod
    @nested_commit_on_success
    def create(cls, bank_type, bank_id, bank_currency, bank_amount, user_id, comment, payment_amount, payment_currency):

        cls.check_types(bank_type=(bank_type, rels.Record),
                        bank_id=(bank_id, int),
                        bank_currency=(bank_currency, rels.Record),
                        bank_amount=(bank_amount, int),
                        user_id=(user_id, basestring),
                        comment=(comment, basestring),
                        payment_amount=(payment_amount, Decimal),
                        payment_currency=(payment_currency, rels.Record))

        model = cls._model_class.objects.create(bank_type=bank_type,
                                                bank_id=bank_id,
                                                bank_currency=bank_currency,
                                                bank_amount=bank_amount,
                                                user_id=user_id,
                                                comment=comment,
                                                payment_amount=payment_amount,
                                                payment_currency=payment_currency,
                                                state=INVOICE_STATE.REQUESTED)

        prototype = cls(model=model)

        return prototype

    @property
    def simple_payment_url(self):
        query = urllib.urlencode({'project': dengionline_settings.PROJECT_ID,
                                  'source': dengionline_settings.PROJECT_ID,
                                  'amount': self.payment_amount,
                                  'nickname': self.user_id.encode('cp1251'),
                                  'orderid': self.id,
                                  'comment': self.comment.encode('cp1251'),
                                  'paymentCurrency': self.payment_currency.url_code})
        url = '%s?%s' % (dengionline_settings.SIMPLE_PAYMENT_URL, query)
        return url


    @classmethod
    def confirm_request_key(cls, amount, user_id, payment_id):
        string = u'%s%s%s%s' % (amount, user_id, payment_id, dengionline_settings.SECRET_KEY)
        return md5.new(string.encode('cp1251')).hexdigest()

    @classmethod
    def check_user_request_key(cls, user_id):
        string = u'%s%s%s%s' % (0, user_id, 0, dengionline_settings.SECRET_KEY)
        return md5.new(string.encode('cp1251')).hexdigest()

    @classmethod
    def check_user(cls, user_id, key):
        if key != cls.check_user_request_key(user_id):
            return CHECK_USER_RESULT.WRONG_KEY

        if cls._model_class.objects.filter(state=INVOICE_STATE.REQUESTED, user_id=user_id).exists():
            return CHECK_USER_RESULT.USER_EXISTS

        return CHECK_USER_RESULT.USER_NOT_EXISTS

    @classmethod
    def confirm_payment(cls, order_id, received_amount, user_id, paymode, payment_id, key):
        from bank.workers.environment import workers_environment

        cls.check_types(order_id=(order_id, int),
                        received_amount=(received_amount, Decimal),
                        user_id=(user_id, basestring),
                        paymode=(paymode, int),
                        payment_id=(payment_id, int),
                        key=(key, basestring))

        user_id = user_id.decode('utf-8').encode('cp1251')

        invoice = cls.get_by_id(int(order_id))

        if invoice is None:
            return CONFIRM_PAYMENT_RESULT.INVOICE_NOT_FOUND

        with nested_commit_on_success():
            confirm_result = invoice.confirm(order_id=int(order_id),
                                             received_amount=Decimal(received_amount),
                                             received_currency=CURRENCY_TYPE._index_name[dengionline_settings.RECEIVED_CURRENCY_TYPE],
                                             user_id=user_id,
                                             payment_id=int(payment_id),
                                             key=key,
                                             paymode=int(paymode))

        if confirm_result._is_CONFIRMED:
            workers_environment.dengionline_banker.cmd_handle_confirmations()

        return confirm_result

    def confirm(self, order_id, received_amount, received_currency, user_id, payment_id, key, paymode):

        if order_id != self.id:
            return CONFIRM_PAYMENT_RESULT.WRONG_ORDER_ID

        if user_id != self.user_id:
            return CONFIRM_PAYMENT_RESULT.WRONG_USER_ID

        real_key = self.confirm_request_key(amount=received_amount, user_id=user_id, payment_id=payment_id)
        if real_key != key:
            return CONFIRM_PAYMENT_RESULT.WRONG_HASH_KEY

        if self.state._is_CONFIRMED:
            # does not check received_amount and received_currency since they can be changed by dengionline configuration
            if self.payment_id != payment_id or self.paymode != paymode:
                return CONFIRM_PAYMENT_RESULT.ALREADY_CONFIRMED_WRONG_ARGUMENTS
            return CONFIRM_PAYMENT_RESULT.ALREADY_CONFIRMED

        if self.state._is_PROCESSED:
            # does not check received_amount and received_currency since they can be changed by dengionline configuration
            if self.payment_id != payment_id or self.paymode != paymode:
                return CONFIRM_PAYMENT_RESULT.ALREADY_PROCESSED_WRONG_ARGUMENTS
            return CONFIRM_PAYMENT_RESULT.ALREADY_PROCESSED

        if self.state._is_DISCARDED:
            return CONFIRM_PAYMENT_RESULT.DISCARDED

        if not self.state._is_REQUESTED:
            # all states MUST be processed before this line
            raise exceptions.WrongInvoiceStateInConfirmationError(state=self.state)

        if self._db_filter(payment_id=str(payment_id)).exists():
            return CONFIRM_PAYMENT_RESULT.DUPLICATED_PAYMENT_ID

        self._model.received_amount = received_amount
        self._model.received_currency = received_currency
        self._model.payment_id = str(payment_id)
        self._model.paymode = paymode
        self._model.state = INVOICE_STATE.CONFIRMED

        self.save()

        return CONFIRM_PAYMENT_RESULT.CONFIRMED

    def process(self):
        from bank.transaction import Transaction
        from bank.relations import ENTITY_TYPE

        if not self.state._is_CONFIRMED:
            raise exceptions.WrongInvoiceStateInProcessingError(invoice_id=self.id, state=self.state)

        transaction = Transaction.create(recipient_type=self.bank_type,
                                         recipient_id=self.bank_id,
                                         sender_type=ENTITY_TYPE.DENGI_ONLINE,
                                         sender_id=0,
                                         currency=self.bank_currency,
                                         amount=self.bank_amount,
                                         description=u'Покупка печенек',
                                         operation_uid='bank-dengionline',
                                         force=True)

        self._model.bank_invoice_id = transaction.invoice_id
        self._model.state = INVOICE_STATE.PROCESSED
        self.save()

    @classmethod
    def discard_old_invoices(cls):
        cls._model_class.objects.filter(state=INVOICE_STATE.REQUESTED,
                                        created_at__lt=datetime.now() - dengionline_settings.DISCARD_TIMEOUT).update(state=INVOICE_STATE.DISCARDED)


    @classmethod
    def process_confirmed_invoices(cls):
        for model in cls._model_class.objects.filter(state=INVOICE_STATE.CONFIRMED):
            invoice = cls(model=model)
            invoice.process()

    def save(self):
        self._model.save()
