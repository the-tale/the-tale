# coding: utf-8
import math

from dext.views import handler, validate_argument

from common.utils.resources import Resource
from common.utils.decorators import login_required

from accounts.views import validate_fast_account

from bank.dengionline.transaction import Transaction as DOTransaction
from bank.dengionline.relations import CURRENCY_TYPE as DO_CURRENCY_TYPE

from bank.relations import ENTITY_TYPE, CURRENCY_TYPE

from accounts.payments import price_list
from accounts.payments.conf import payments_settings


class PaymentsResource(Resource):

    @login_required
    @validate_fast_account()
    def initialize(self, *args, **kwargs):
        super(PaymentsResource, self).initialize(*args, **kwargs)

    @handler('shop', method='get')
    def shop(self):
        return self.template('payments/shop.html',
                             {'PRICE_LIST': price_list.PRICE_LIST,
                              'account': self.account,
                              'page_type': 'shop'})

    @handler('history', method='get')
    def history(self):
        history = self.account.bank_account.get_history_list()
        return self.template('payments/history.html',
                             {'page_type': 'history',
                              'account': self.account,
                              'history': history})

    @validate_argument('purchase', price_list.PURCHASES_BY_UID.get, 'payments.buy', u'неверный идентификатор покупки')
    @handler('buy', method='post')
    def buy(self, purchase):
        postponed_task = purchase.buy(account=self.account)
        return self.json_processing(postponed_task.status_url)


    @validate_argument('amount', int, 'payments.pay_with_dengionline', u'Неверная сумма платежа')
    @handler('pay-with-dengionline', method='post')
    def pay_with_dengionline(self, amount): # количество валюты

        if amount <= 0:
            return self.json_error('payments.pay_with_dengionline.wrong_amount_value', u'Размер суммы должен быть больше 0')

        premium_amount = int(math.ceil(amount * payments_settings.PREMIUM_CURRENCY_FOR_DOLLAR))

        transaction = DOTransaction.create(bank_type=ENTITY_TYPE.GAME_ACCOUNT,
                                           bank_id=self.account.id,
                                           bank_currency=CURRENCY_TYPE.PREMIUM,
                                           bank_amount=premium_amount,
                                           email=self.account.email,
                                           comment=u'Покупка печенек: %d шт.' % premium_amount,
                                           payment_amount=amount,
                                           payment_currency=DO_CURRENCY_TYPE.USD)

        return self.json_ok(data={'next_url': transaction.get_simple_payment_url()})
