import functools

from django.core.urlresolvers import reverse

from dext.common.utils import views as dext_views
from dext.common.utils.urls import url
from dext.common.utils.urls import UrlBuilder
from dext.settings import settings

from the_tale.common.utils import views as utils_views
from the_tale.common.utils import pagination

from the_tale.common.postponed_tasks.prototypes import PostponedTaskPrototype

from the_tale.accounts import views as accounts_views
from the_tale.accounts import logic as accounts_logic

from the_tale.accounts.third_party import views as third_party_views

from the_tale.game.heroes import logic as heroes_logic

from the_tale.game.cards import views as cards_views
from the_tale.game.cards import tt_api as cards_tt_api
from the_tale.game.cards import logic as cards_logic
from the_tale.game.cards import relations as cards_relations

from . import price_list
from . import forms
from . import conf
from . import logic
from . import relations
from . import tt_api
from . import objects


########################################
# processors definition
########################################

class XsollaEnabledProcessor(dext_views.BaseViewProcessor):
    def preprocess(self, context):
        real_payments_enabled = (settings.get(conf.payments_settings.SETTINGS_ALLOWED_KEY) and
                                 (conf.payments_settings.ENABLE_REAL_PAYMENTS or
                                  context.account.id in conf.payments_settings.ALWAYS_ALLOWED_ACCOUNTS))

        context.xsolla_enabled = real_payments_enabled and conf.payments_settings.XSOLLA_ENABLED


class PurchaseProcessor(dext_views.ArgumentProcessor):
    ERROR_MESSAGE = 'Неверный идентификатор покупки'
    GET_NAME = 'purchase'
    CONTEXT_NAME = 'purchase'

    def parse(self, context, raw_value):
        id = raw_value

        if id not in price_list.PURCHASES_BY_UID:
            self.raise_wrong_value()

        return price_list.PURCHASES_BY_UID.get(id)


class LotPriceProcessor(dext_views.ArgumentProcessor):
    CONTEXT_NAME = 'price'
    ERROR_MESSAGE = 'Неверная цена лота'
    POST_NAME = 'price'

    def parse(self, context, raw_value):
        price = int(raw_value)

        if price < conf.payments_settings.MINIMUM_MARKET_PRICE:
            self.raise_wrong_value()

        return price


class ItemTypeProcessor(dext_views.ArgumentProcessor):
    CONTEXT_NAME = 'item_type'
    ERROR_MESSAGE = 'Необходимо указать тип товара'
    POST_NAME = 'item_type'

    def parse(self, context, raw_value):
        return raw_value


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

@resource('', method='get')
def index(context):
    hero = heroes_logic.load_hero(account_id=context.account.id)

    return dext_views.Page('shop/shop.html',
                           content={'SUBSCRIPTIONS': price_list.SUBSCRIPTIONS,
                                    'CARD_RARITY': cards_relations.RARITY,
                                    'hero': hero,
                                    'payments_settings': conf.payments_settings,
                                    'account': context.account,
                                    'page_type': 'shop',
                                    'resource': context.resource})


@resource('history', method='get')
def history(context):
    history = context.account.bank_account.get_history_list()

    return dext_views.Page('shop/history.html',
                           content={'SUBSCRIPTIONS': price_list.SUBSCRIPTIONS,
                                    'CARD_RARITY': cards_relations.RARITY,
                                    'page_type': 'shop-history',
                                    'payments_settings': conf.payments_settings,
                                    'permanent_purchases': sorted(context.account.permanent_purchases, key=lambda r: r.text),
                                    'account': context.account,
                                    'history': history,
                                    'resource': context.resource})


@utils_views.PageNumberProcessor()
@resource('market-history', method='get')
def market_history(context):

    cards_info = cards_logic.get_cards_info_by_full_types()

    page, total_records, records = tt_api.history(page=context.page+1, records_on_page=conf.payments_settings.MARKET_HISTORY_RECORDS_ON_PAGE)

    page -= 1

    url_builder = UrlBuilder(reverse('shop:market-history'), arguments={'page': context.page})

    history_paginator = pagination.Paginator(page,
                                             total_records,
                                             conf.payments_settings.MARKET_HISTORY_RECORDS_ON_PAGE,
                                             url_builder)

    return dext_views.Page('shop/market_history.html',
                           content={'SUBSCRIPTIONS': price_list.SUBSCRIPTIONS,
                                    'CARD_RARITY': cards_relations.RARITY,
                                    'page_type': 'market-history',
                                    'payments_settings': conf.payments_settings,
                                    'permanent_purchases': sorted(context.account.permanent_purchases, key=lambda r: r.text),
                                    'account': context.account,
                                    'records': records,
                                    'resource': context.resource,
                                    'paginator': history_paginator,
                                    'cards_info': cards_info})

@PurchaseProcessor()
@resource('buy', method='post')
def buy(context):
    postponed_task = context.purchase.buy(account=context.account)
    return dext_views.AjaxProcessing(postponed_task.status_url)


@cards_views.AccountCardsLoader()
@cards_views.AccountCardsProcessor()
@LotPriceProcessor()
@resource('create-sell-lot', method='post')
def create_sell_lot(context):

    if not all(card.available_for_auction for card in context.cards):
        raise dext_views.ViewError(code='not_available_for_auction', message='Как минимум одна из карт не может быть продана на аукционе')

    lots = []
    for card in context.cards:
        lots.append(objects.Lot(owner_id=context.account.id,
                                full_type=card.item_full_type,
                                item_id=card.uid,
                                price=context.price))

    cards_tt_api.change_cards_owner(old_owner_id=context.account.id,
                                    new_owner_id=accounts_logic.get_system_user_id(),
                                    operation_type='#create_sell_lots',
                                    new_storage_id=0,
                                    cards_ids=[card.uid for card in context.cards])

    tt_api.place_sell_lots(lots)

    return dext_views.AjaxOk()


@ItemTypeProcessor()
@LotPriceProcessor()
@resource('close-sell-lot', method='post')
def close_sell_lot(context):

    if context.account.bank_account.amount < context.price:
        raise dext_views.ViewError(code='not_enough_money', message='Не хватает средств для покупки')

    task = logic.close_lot(item_type=context.item_type,
                           price=context.price,
                           buyer_id=context.account.id)
    postponed_task = PostponedTaskPrototype.create(task)
    postponed_task.cmd_wait()

    return dext_views.AjaxProcessing(postponed_task.status_url)


@ItemTypeProcessor()
@LotPriceProcessor()
@resource('cancel-sell-lot', method='post')
def cancel_sell_lot(context):

    lots = tt_api.cancel_lot(item_type=context.item_type,
                             price=context.price,
                             owner_id=context.account.id)

    if not lots:
        return dext_views.AjaxOk()

    cards_tt_api.change_cards_owner(old_owner_id=accounts_logic.get_system_user_id(),
                                    new_owner_id=context.account.id,
                                    operation_type='#cancel_sell_lots',
                                    new_storage_id=0,
                                    cards_ids=[lot.item_id for lot in lots])

    return dext_views.AjaxOk()


@resource('info', method='get')
def info(context):
    info = tt_api.info(owner_id=context.account.id)

    cards_info = cards_logic.get_cards_info_by_full_types()

    for summary in info:
        card_info = cards_info[summary.full_type]

        summary.name = card_info['name']
        summary.type = card_info['card'].value

    return dext_views.AjaxOk(content={'info': [summary.ui_info() for summary in info],
                                      'account_balance': context.account.bank_account.amount})


@dext_views.ArgumentProcessor(error_message='Необходимо указать тип товара', get_name='item_type', context_name='item_type')
@resource('item-type-prices', method='get')
def item_type_prices(context):
    prices, owner_prices = tt_api.item_type_prices(context.item_type, owner_id=context.account.id)
    return dext_views.AjaxOk(content={'prices': prices,
                                      'owner_prices': owner_prices})


@accounts_views.SuperuserProcessor()
@accounts_views.AccountProcessor(get_name='account', context_name='target_account', error_message='Аккаунт не обнаружен')
@dext_views.FormProcessor(form_class=forms.GMForm)
@resource('give-money', method='post')
def give_money(context):

    if context.target_account.is_fast:
        raise dext_views.ViewError(code='fast_account', message='Нельзя начислить деньги «быстрому» аккаунту')

    logic.transaction_gm(account=context.target_account,
                         amount=context.form.c.amount,
                         description=context.form.c.description,
                         game_master=context.account)

    return dext_views.AjaxOk()
