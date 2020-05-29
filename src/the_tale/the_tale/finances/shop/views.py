
import smart_imports

smart_imports.all()


########################################
# processors definition
########################################

class XsollaEnabledProcessor(utils_views.BaseViewProcessor):
    def preprocess(self, context):
        real_payments_enabled = (global_settings.get(conf.settings.SETTINGS_ALLOWED_KEY) and
                                 (conf.settings.ENABLE_REAL_PAYMENTS or
                                  context.account.id in conf.settings.ALWAYS_ALLOWED_ACCOUNTS))

        context.xsolla_enabled = real_payments_enabled and conf.settings.XSOLLA_ENABLED


class PurchaseProcessor(utils_views.ArgumentProcessor):
    ERROR_MESSAGE = 'Неверный идентификатор покупки'
    GET_NAME = 'purchase'
    CONTEXT_NAME = 'purchase'

    def parse(self, context, raw_value):
        id = raw_value

        if id not in price_list.PURCHASES_BY_UID:
            self.raise_wrong_value()

        return price_list.PURCHASES_BY_UID.get(id)


class LotPriceProcessor(utils_views.IntArgumentProcessor):
    CONTEXT_NAME = 'price'
    ERROR_MESSAGE = 'Неверная цена лота'
    POST_NAME = 'price'


class ItemTypeProcessor(utils_views.ArgumentProcessor):
    CONTEXT_NAME = 'item_type'
    ERROR_MESSAGE = 'Необходимо указать тип товара'
    POST_NAME = 'item_type'

    def parse(self, context, raw_value):
        return raw_value


########################################
# resource and global processors
########################################
resource = utils_views.Resource(name='shop')
resource.add_processor(accounts_views.CurrentAccountProcessor())
resource.add_processor(utils_views.FakeResourceProcessor())
resource.add_processor(accounts_views.LoginRequiredProcessor())
resource.add_processor(accounts_views.FullAccountProcessor())
resource.add_processor(accounts_views.BanGameProcessor())
resource.add_processor(third_party_views.RefuseThirdPartyProcessor())
resource.add_processor(XsollaEnabledProcessor())


@resource('', method='get')
def index(context):

    payment_successed = False
    payment_failed = False

    if 'status' in context.django_request.GET:
        payment_successed = context.django_request.GET.get('status') == 'done'
        payment_failed = context.django_request.GET.get('status') != 'done'

    hero = heroes_logic.load_hero(account_id=context.account.id)

    return utils_views.Page('shop/shop.html',
                           content={'SUBSCRIPTIONS': price_list.SUBSCRIPTIONS,
                                    'CARD_RARITY': cards_relations.RARITY,
                                    'CARDS_MIN_PRICES': relations.CARDS_MIN_PRICES,
                                    'JS_CARDS_MIN_PRICES': {rarity.value: price for rarity, price in relations.CARDS_MIN_PRICES.items()},
                                    'hero': hero,
                                    'payments_settings': conf.settings,
                                    'account': context.account,
                                    'page_type': 'shop',
                                    'resource': context.resource,
                                    'payment_successed': payment_successed,
                                    'payment_failed': payment_failed})


@resource('history', method='get')
def history(context):
    history = context.account.bank_account.get_history_list()

    return utils_views.Page('shop/history.html',
                           content={'SUBSCRIPTIONS': price_list.SUBSCRIPTIONS,
                                    'CARD_RARITY': cards_relations.RARITY,
                                    'page_type': 'shop-history',
                                    'payments_settings': conf.settings,
                                    'permanent_purchases': sorted(context.account.permanent_purchases, key=lambda r: r.text),
                                    'account': context.account,
                                    'history': history,
                                    'resource': context.resource})


@utils_views.PageNumberProcessor()
@resource('market-history', method='get')
def market_history(context):

    cards_info = cards_logic.get_cards_info_by_full_types()

    page, total_records, records = tt_services.market.cmd_history(page=context.page + 1, records_on_page=conf.settings.MARKET_HISTORY_RECORDS_ON_PAGE)

    page -= 1

    url_builder = utils_urls.UrlBuilder(django_reverse('shop:market-history'), arguments={'page': context.page})

    history_paginator = utils_pagination.Paginator(page,
                                                   total_records,
                                                   conf.settings.MARKET_HISTORY_RECORDS_ON_PAGE,
                                                   url_builder)

    return utils_views.Page('shop/market_history.html',
                           content={'SUBSCRIPTIONS': price_list.SUBSCRIPTIONS,
                                    'CARD_RARITY': cards_relations.RARITY,
                                    'page_type': 'market-history',
                                    'payments_settings': conf.settings,
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
    return utils_views.AjaxProcessing(postponed_task.status_url)


@cards_views.AccountCardsLoader()
@cards_views.AccountCardsProcessor()
@LotPriceProcessor()
@resource('create-sell-lot', method='post')
def create_sell_lot(context):

    if not all(card.available_for_auction for card in context.cards):
        raise utils_views.ViewError(code='not_available_for_auction', message='Как минимум одна из карт не может быть продана на аукционе')

    for card in context.cards:
        if context.price < relations.CARDS_MIN_PRICES[card.type.rarity]:
            raise utils_views.ViewError(code='too_small_price',
                                       message='Цена продажи меньше чем минимально разрешённая цена продажи как минимум у одной карты')

        if conf.settings.MAX_PRICE < context.price:
            raise utils_views.ViewError(code='too_large_price',
                                       message='Цена продажи больше чем максимально разрешённая ({max_price}) как минимум у одной карты'.format(max_price=conf.settings.MAX_PRICE))

    logic.create_lots(owner_id=context.account.id,
                      cards=context.cards,
                      price=context.price)

    return utils_views.AjaxOk()


@ItemTypeProcessor()
@LotPriceProcessor()
@resource('close-sell-lot', method='post')
def close_sell_lot(context):

    if context.account.bank_account.amount < context.price:
        raise utils_views.ViewError(code='not_enough_money', message='Не хватает средств для покупки')

    task = logic.close_lot(item_type=context.item_type,
                           price=context.price,
                           buyer_id=context.account.id)
    postponed_task = PostponedTaskPrototype.create(task)
    postponed_task.cmd_wait()

    return utils_views.AjaxProcessing(postponed_task.status_url)


@ItemTypeProcessor()
@LotPriceProcessor()
@resource('cancel-sell-lot', method='post')
def cancel_sell_lot(context):

    logic.cancel_sell_lot(item_type=context.item_type,
                          price=context.price,
                          account_id=context.account.id,
                          operation_type='#cancel_sell_lots')

    return utils_views.AjaxOk()


@resource('info', method='get')
def info(context):
    info = tt_services.market.cmd_info(owner_id=context.account.id)

    cards_info = cards_logic.get_cards_info_by_full_types()

    for summary in info:
        card_info = cards_info[summary.full_type]

        summary.name = card_info['name']
        summary.type = card_info['card'].value

    return utils_views.AjaxOk(content={'info': [summary.ui_info() for summary in info],
                                       'account_balance': context.account.bank_account.amount})


@utils_views.ArgumentProcessor(error_message='Необходимо указать тип товара', get_name='item_type', context_name='item_type')
@resource('item-type-prices', method='get')
def item_type_prices(context):
    prices, owner_prices = tt_services.market.cmd_item_type_prices(context.item_type, owner_id=context.account.id)
    return utils_views.AjaxOk(content={'prices': prices,
                                      'owner_prices': owner_prices})


@accounts_views.SuperuserProcessor()
@accounts_views.AccountProcessor(get_name='account', context_name='target_account', error_message='Аккаунт не обнаружен')
@utils_views.FormProcessor(form_class=forms.GMForm)
@resource('give-money', method='post')
def give_money(context):

    if context.target_account.is_fast:
        raise utils_views.ViewError(code='fast_account', message='Нельзя начислить деньги «быстрому» аккаунту')

    logic.transaction_gm(account=context.target_account,
                         amount=context.form.c.amount,
                         description=context.form.c.description,
                         game_master=context.account)

    return utils_views.AjaxOk()
