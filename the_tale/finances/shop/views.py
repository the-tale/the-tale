# coding: utf-8
from dext.common.utils import views as dext_views
from dext.common.utils.urls import url
from dext.settings import settings

from the_tale.common.utils import views as utils_views

from the_tale.accounts import views as accounts_views

from the_tale.finances.shop import price_list
from the_tale.finances.shop.forms import GMForm
from the_tale.finances.shop.conf import payments_settings
from the_tale.finances.shop.logic import transaction_gm
from the_tale.finances.shop import relations

from the_tale.accounts.third_party import views as third_party_views

from the_tale.game.heroes import logic as heroes_logic

########################################
# processors definition
########################################

class XsollaEnabledProcessor(dext_views.BaseViewProcessor):
    def preprocess(self, context):
        real_payments_enabled = (settings.get(payments_settings.SETTINGS_ALLOWED_KEY) and
                                 (payments_settings.ENABLE_REAL_PAYMENTS or
                                  context.account.id in payments_settings.ALWAYS_ALLOWED_ACCOUNTS))

        context.xsolla_enabled = real_payments_enabled and payments_settings.XSOLLA_ENABLED

class PurchaseProcessor(dext_views.ArgumentProcessor):
    ERROR_MESSAGE = u'Неверный идентификатор покупки'
    GET_NAME = 'purchase'
    CONTEXT_NAME = 'purchase'

    def parse(self, context, raw_value):
        id = raw_value

        if id not in price_list.PURCHASES_BY_UID:
            self.raise_wrong_value()

        return price_list.PURCHASES_BY_UID.get(id)

########################################
# resource and global processors
########################################
resource = dext_views.Resource(name='shop')
resource.add_processor(accounts_views.CurrentAccountProcessor())
resource.add_processor(utils_views.FakeResourceProcessor())
resource.add_processor(accounts_views.LoginRequiredProcessor())
resource.add_processor(accounts_views.FullAccountProcessor())
resource.add_processor(accounts_views.BanGameProcessor())
resource.add_processor(third_party_views.RefuseThirdPartyProcessor())
resource.add_processor(XsollaEnabledProcessor())

@resource('')
def index(context):
    if context.account.is_premium:
        return dext_views.Redirect(target_url=url('market:'))
    return dext_views.Redirect(target_url=url('shop:shop'))

@resource('shop', method='get')
def shop(context):
    hero = heroes_logic.load_hero(account_id=context.account.id)

    if context.account.is_premium:
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

        return choices.get((x.type, y.type, context.account.is_premium), cmp(price_types.index(x.type), price_types.index(y.type)))

    price_groups = sorted(price_list.PRICE_GROUPS, cmp=_cmp)

    return dext_views.Page('shop/shop.html',
                           content={'PRICE_GROUPS': price_groups,
                                    'hero': hero,
                                    'payments_settings': payments_settings,
                                    'account': context.account,
                                    'featured_group': featured_group,
                                    'page_type': 'shop',
                                    'resource': context.resource})


@resource('history', method='get')
def history(context):
    history = context.account.bank_account.get_history_list()
    return dext_views.Page('shop/history.html',
                           content={'page_type': 'shop-history',
                                    'payments_settings': payments_settings,
                                    'permanent_purchases': sorted(context.account.permanent_purchases, key=lambda r: r.text),
                                    'account': context.account,
                                    'history': history,
                                    'resource': context.resource})

@PurchaseProcessor()
@resource('buy', method='post')
def buy(context):
    postponed_task = context.purchase.buy(account=context.account)
    return dext_views.AjaxProcessing(postponed_task.status_url)


@accounts_views.SuperuserProcessor()
@accounts_views.AccountProcessor(get_name='account', context_name='target_account', error_message=u'Аккаунт не обнаружен')
@dext_views.FormProcessor(form_class=GMForm)
@resource('give-money', method='post')
def give_money(context):

    if context.target_account.is_fast:
        raise dext_views.ViewError(code='fast_account', message=u'Нельзя начислить деньги «быстрому» аккаунту')

    transaction_gm(account=context.target_account,
                   amount=context.form.c.amount,
                   description=context.form.c.description,
                   game_master=context.account)

    return dext_views.AjaxOk()
