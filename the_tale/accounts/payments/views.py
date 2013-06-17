# coding: utf-8

from dext.views import handler, validate_argument, validator

from common.utils.resources import Resource
from common.utils.decorators import login_required, superuser_required

from accounts.views import validate_fast_account

from bank.dengionline.transaction import Transaction as DOTransaction
from bank.dengionline.relations import CURRENCY_TYPE as DO_CURRENCY_TYPE

from bank.relations import ENTITY_TYPE, CURRENCY_TYPE
from bank.dengionline import exceptions

from accounts.prototypes import AccountPrototype

from accounts.payments import price_list
from accounts.payments.forms import DengiOnlineForm, GMForm
from accounts.payments.conf import payments_settings
from accounts.payments.logic import real_amount_to_game, transaction_gm


class PaymentsResource(Resource):

    @login_required
    @validate_fast_account()
    def initialize(self, *args, **kwargs):
        super(PaymentsResource, self).initialize(*args, **kwargs)

        self.dengionline_enabled = (payments_settings.ENABLE_REAL_PAYMENTS or
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

    @handler('successed', method='get')
    def successed(self):
        return self.template('payments/successed.html',
                             {'account': self.account,
                              'page_type': 'successed'})

    @handler('failed', method='get')
    def failed(self):
        return self.template('payments/failed.html',
                             {'account': self.account,
                              'page_type': 'failed'})

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
                                               comment=u'Покупка печенек: %d шт. за %d$' % (form.c.game_amount, form.c.real_amount),
                                               payment_amount=form.c.real_amount,
                                               payment_currency=DO_CURRENCY_TYPE.USD)
        except exceptions.CreationLimitError:
            return self.json_error('payments.pay_with_dengionline.creation_limit_riched',
                                   u'Вы создали слишком много запросов на покупку печенек. Вы сможете повторить попытку через несколько минут.')

        return self.json_ok(data={'next_url': transaction.get_simple_payment_url()})

    @superuser_required()
    @validate_argument('account', AccountPrototype.get_by_id, 'payments.give_money', u'Аккаунт не обнаружен')
    @handler('give-money', method='post')
    def give_money(self, account):

        if account.is_fast:
            return self.json_error('payments.give_money.fast_account', u'Нельзя начислить деньги «быстрому» аккаунту')

        form = GMForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('payments.give_money.form_errors', form.errors)

        transaction_gm(account=account,
                       amount=form.c.amount,
                       description=form.c.description,
                       game_master=self.account)

        return self.json_ok()
