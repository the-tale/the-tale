# coding: utf-8
import md5
import urllib

from common.utils.prototypes import BasePrototype

from bank.dengionline.models import Invoice
from bank.dengionline.conf import dengionline_settings
from bank.dengionline.relations import INVOICE_STATE, CHECK_USER_RESULT
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
    def create(cls, bank_type, bank_id, bank_currency, bank_amount, user_id, comment, payment_amount, payment_currency):

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

    # TODO: what if dengionline send 2 simultaneous requests ?
    def confirm(self, order_id, received_amount, received_currency, user_id, payment_id, key, paymode):

        if order_id != self.id:
            raise exceptions.WrongOrderIdInConfirmationError(invoice_id=self.id, order_id=order_id)

        if user_id != self.user_id:
            raise exceptions.WrongUserIdInConfirmationError(invoice_id=self.id,  user_id=user_id)

        real_key = self.confirm_request_key(amount=received_amount, user_id=user_id, payment_id=payment_id)
        if real_key != key:
            raise exceptions.WrongRequestKeyInConfirmationError(invoice_id=self.id, key=key)

        if self.payment_id is not None:
            raise exceptions.InvoiceAlreadyConfirmedError(invoice_id=self.id)

        self._model.received_amount = received_amount
        self._model.received_currency = received_currency
        self._model.payment_id = str(payment_id)
        self._model.paymode = paymode
        self._model.state = INVOICE_STATE.CONFIRMED

        self.save()

    def save(self):
        self._model.save()
