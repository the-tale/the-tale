# coding: utf-8
import md5

from dext.views import handler, validate_argument, validator
from dext.settings import settings
from dext.common.utils.urls import UrlBuilder

from the_tale.common.utils.resources import Resource
from the_tale.common.utils.decorators import login_required, superuser_required

from the_tale.accounts.views import validate_fast_account

from the_tale.accounts.prototypes import AccountPrototype

from the_tale.accounts.payments import price_list
from the_tale.accounts.payments.forms import GMForm
from the_tale.accounts.payments.conf import payments_settings
from the_tale.accounts.payments.logic import real_amount_to_game, transaction_gm
from the_tale.accounts.payments import relations

from the_tale.game.heroes.prototypes import HeroPrototype

from the_tale.accounts.third_party import decorators


class PaymentsResource(Resource):

    XSOLLA_DIALOG_WIDTH = payments_settings.XSOLLA_DIALOG_WIDTH
    XSOLLA_DIALOG_HEIGHT = payments_settings.XSOLLA_DIALOG_HEIGHT

    @decorators.refuse_third_party
    @login_required
    @validate_fast_account()
    def initialize(self, *args, **kwargs):
        super(PaymentsResource, self).initialize(*args, **kwargs)

        self.real_payments_enabled = ( settings.get(payments_settings.SETTINGS_ALLOWED_KEY) and
                                     (payments_settings.ENABLE_REAL_PAYMENTS or
                                      self.account.id in payments_settings.ALWAYS_ALLOWED_ACCOUNTS))

        self.xsolla_enabled = self.real_payments_enabled and payments_settings.XSOLLA_ENABLED

        self.usd_to_premium = real_amount_to_game(1)


    @property
    def xsolla_paystaion_widget_link(self):
        # TODO: sign
        url_builder = UrlBuilder(base=payments_settings.XSOLLA_BASE_LINK)

        sign_params = {'v1': self.account.email,
                      'email': self.account.email,
                      payments_settings.XSOLLA_ID_THEME: payments_settings.XSOLLA_THEME,
                      'project': payments_settings.XSOLLA_PROJECT}

        sign_md5 = md5.new(''.join(sorted(u'%s=%s' % (k, v) for k,v in sign_params.iteritems()))).hexdigest()

        attributes = {'v1': self.account.email,
                      'email': self.account.email,
                      payments_settings.XSOLLA_ID_THEME: payments_settings.XSOLLA_THEME,
                      'project': payments_settings.XSOLLA_PROJECT,
                      'local': payments_settings.XSOLLA_LOCAL,
                      'description': payments_settings.XSOLLA_DESCRIPTION,
                      'sign': sign_md5}

        if payments_settings.XSOLLA_MARKETPLACE is not None:
            attributes['marketplace'] = payments_settings.XSOLLA_MARKETPLACE

        if payments_settings.XSOLLA_PID is not None:
            attributes['pid'] = payments_settings.XSOLLA_PID

        link = url_builder(**attributes)

        return link

    @validator('payments.xsolla_disabled', u'Платежи c помощью «Xsolla» отключены')
    def validate_xsolla_enabled(self, *args, **kwargs): return self.xsolla_enabled

    @handler('shop', method='get')
    def shop(self):
        hero = HeroPrototype.get_by_account_id(self.account.id)

        if self.account.is_premium:
            featured_group = relations.GOODS_GROUP.CHEST
        else:
            featured_group = relations.GOODS_GROUP.PREMIUM

        price_types = [group.type for group in price_list.PRICE_GROUPS]

        def _cmp(x, y):
            choices = { (relations.GOODS_GROUP.PREMIUM, relations.GOODS_GROUP.CHEST, False): -1,
                        (relations.GOODS_GROUP.PREMIUM, relations.GOODS_GROUP.CHEST, True): 1,
                        (relations.GOODS_GROUP.CHEST, relations.GOODS_GROUP.PREMIUM, False): 1,
                        (relations.GOODS_GROUP.CHEST, relations.GOODS_GROUP.PREMIUM, True): -1,

                        (relations.GOODS_GROUP.PREMIUM, relations.GOODS_GROUP.ENERGY, False): -1,
                        (relations.GOODS_GROUP.PREMIUM, relations.GOODS_GROUP.ENERGY, True): 1,
                        (relations.GOODS_GROUP.ENERGY, relations.GOODS_GROUP.PREMIUM, False): 1,
                        (relations.GOODS_GROUP.ENERGY, relations.GOODS_GROUP.PREMIUM, True): -1 }

            return choices.get((x.type, y.type, self.account.is_premium), cmp(price_types.index(x.type), price_types.index(y.type)))

        price_groups = sorted(price_list.PRICE_GROUPS, cmp=_cmp)

        return self.template('payments/shop.html',
                             {'PRICE_GROUPS': price_groups,
                              'hero': hero,
                              'payments_settings': payments_settings,
                              'account': self.account,
                              'featured_group': featured_group,
                              'page_type': 'shop'})

    @handler('history', method='get')
    def history(self):
        history = self.account.bank_account.get_history_list()
        return self.template('payments/history.html',
                             {'page_type': 'history',
                              'payments_settings': payments_settings,
                              'account': self.account,
                              'history': history})

    @handler('purchases', method='get')
    def purchases(self):
        return self.template('payments/purchases.html',
                             {'page_type': 'purchases',
                              'payments_settings': payments_settings,
                              'permanent_purchases': sorted(self.account.permanent_purchases, key=lambda r: r.text),
                              'account': self.account})

    @validate_argument('purchase', price_list.PURCHASES_BY_UID.get, 'payments.buy', u'неверный идентификатор покупки')
    @handler('buy', method='post')
    def buy(self, purchase):
        postponed_task = purchase.buy(account=self.account)
        return self.json_processing(postponed_task.status_url)

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
