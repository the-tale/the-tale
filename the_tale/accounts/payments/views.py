# coding: utf-8

from dext.views import handler, validate_argument

from common.utils.resources import Resource
from common.utils.decorators import login_required

from accounts.views import validate_fast_account

from accounts.payments import price_list


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

    @validate_argument('purchase', price_list.PURCHASES_BY_UID.get, 'payments', u'неверный идентификатор покупки')
    @handler('buy', method='post')
    def buy(self, purchase):
        postponed_task = purchase.buy(account=self.account)
        return self.json_processing(postponed_task.status_url)
