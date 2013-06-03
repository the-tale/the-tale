# coding: utf-8

from dext.views import handler, validate_argument, validator

from common.utils.resources import Resource
from common.utils.decorators import login_required

from accounts.views import validate_fast_account

from bank.dengionline.transaction import Transaction as DOTransaction
from bank.dengionline.relations import CURRENCY_TYPE as DO_CURRENCY_TYPE

from bank.relations import ENTITY_TYPE, CURRENCY_TYPE
from bank.dengionline import exceptions

from accounts.payments import price_list
from accounts.payments.forms import DengiOnlineForm
from accounts.payments.conf import payments_settings
from accounts.payments.logic import real_amount_to_game


class PaymentsResource(Resource):

    @login_required
    @validate_fast_account()
    def initialize(self, *args, **kwargs):
        super(PaymentsResource, self).initialize(*args, **kwargs)

        self.dengionline_enabled = (payments_settings.ENABLE_DENGIONLINE or
                                    self.account.id in payments_settings.ALWAYS_ALLOWED_ACCOUNTS)

        self.usd_to_premium = real_amount_to_game(1)

    @validator('payments.dengionline_disabled', u'Платежи c помощью «Деньги Онлайн» отключены')
    def validate_dengionline_enabled(self, *args, **kwargs): return self.dengionline_enabled

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


    @validate_dengionline_enabled()
    @handler('pay-dialog', method='get')
    def pay_dialog(self):
        return self.template('payments/pay_dialog.html',
                             {'dengionline_form': DengiOnlineForm(),
                              'cource': real_amount_to_game(1)})

    @validate_dengionline_enabled()
    @handler('pay-with-dengionline', method='post')
    def pay_with_dengionline(self):

        form = DengiOnlineForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('payments.pay_with_dengionline.form_errors', form.errors)

        try:
            transaction = DOTransaction.create(bank_type=ENTITY_TYPE.GAME_ACCOUNT,
                                               bank_id=self.account.id,
                                               bank_currency=CURRENCY_TYPE.PREMIUM,
                                               bank_amount=form.c.game_amount,
                                               email=self.account.email,
                                               comment=u'Покупка печенек: %d шт.' % form.c.real_amount,
                                               payment_amount=form.c.real_amount,
                                               payment_currency=DO_CURRENCY_TYPE.USD)
        except exceptions.CreationLimitError:
            return self.json_error('payments.pay_with_dengionline.creation_limit_riched',
                                   u'Вы создали слишком много запросов на покупку печенек. Вы сможете повторить попытку через несколько минут.')

        return self.json_ok(data={'next_url': transaction.get_simple_payment_url()})
