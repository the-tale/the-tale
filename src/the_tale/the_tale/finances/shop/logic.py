
import smart_imports

smart_imports.all()


def create_sell_lot_url():
    return utils_urls.url('shop:create-sell-lot')


def close_sell_lot_url():
    return utils_urls.url('shop:close-sell-lot')


def cancel_sell_lot_url():
    return utils_urls.url('shop:cancel-sell-lot')


def info_url():
    return utils_urls.url('shop:info')


def item_type_prices_url():
    return utils_urls.url('shop:item-type-prices')


def real_amount_to_game(amount):
    return int(math.ceil(amount * conf.settings.PREMIUM_CURRENCY_FOR_DOLLAR))


def transaction_logic(account, amount, description, uid, force=False):
    return bank_transaction.Transaction.create(recipient_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                                               recipient_id=account.id,
                                               sender_type=bank_relations.ENTITY_TYPE.GAME_LOGIC,
                                               sender_id=0,
                                               currency=bank_relations.CURRENCY_TYPE.PREMIUM,
                                               amount=amount,
                                               description_for_sender=description,
                                               description_for_recipient=description,
                                               operation_uid=uid,
                                               force=force)


def transaction_gm(account, amount, description, game_master):

    return bank_transaction.Transaction.create(recipient_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                                               recipient_id=account.id,
                                               sender_type=bank_relations.ENTITY_TYPE.GAME_MASTER,
                                               sender_id=game_master.id,
                                               currency=bank_relations.CURRENCY_TYPE.PREMIUM,
                                               amount=amount,
                                               description_for_sender=description,
                                               description_for_recipient=description,
                                               operation_uid='game-master-gift',
                                               force=True)


class PermanentRelationsStorage(utils_permanent_storage.PermanentRelationsStorage):
    RELATION = relations.PERMANENT_PURCHASE_TYPE
    VALUE_COLUMN = 'value'


def create_lots(owner_id, cards, price):
    lots = []

    for card in cards:
        lots.append(objects.Lot(owner_id=owner_id,
                                full_type=card.item_full_type,
                                item_id=card.uid,
                                price=price))

    cards_logic.change_owner(old_owner_id=owner_id,
                             new_owner_id=accounts_logic.get_system_user_id(),
                             operation_type='#create_sell_lots',
                             new_storage=cards_relations.STORAGE.FAST,
                             cards_ids=[card.uid for card in cards])

    tt_services.market.cmd_place_sell_lots(lots)


def close_lot(item_type, price, buyer_id):
    cards_info = cards_logic.get_cards_info_by_full_types()

    name = cards_info[item_type]['name']

    invoice = bank_prototypes.InvoicePrototype.create(recipient_type=bank_relations.ENTITY_TYPE.GAME_LOGIC,
                                                      recipient_id=0,
                                                      sender_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                                                      sender_id=buyer_id,
                                                      currency=bank_relations.CURRENCY_TYPE.PREMIUM,
                                                      amount=price,
                                                      description_for_sender='Покупка «%s»' % name,
                                                      description_for_recipient='Продажа «%s»' % name,
                                                      operation_uid='market-buy-lot-cards-hero-good')

    transaction = bank_transaction.Transaction(invoice.id)

    return postponed_tasks.BuyMarketLot(account_id=buyer_id,
                                        price=price,
                                        item_type=item_type,
                                        transaction=transaction)


def cancel_lots_by_type(item_type):
    lots = tt_services.market.cmd_cancel_lots_by_type(item_type=item_type)

    for lot in lots:
        try:
            cards_logic.change_owner(old_owner_id=accounts_logic.get_system_user_id(),
                                     new_owner_id=lot.owner_id,
                                     operation_type='#cancel_sell_lots',
                                     new_storage=cards_relations.STORAGE.FAST,
                                     cards_ids=[lot.item_id])
        except Exception as e:
            print(e)

    return lots


def get_commission(price):
    commission = int(math.floor(price * conf.settings.MARKET_COMISSION))

    if commission == 0:
        commission = 1

    return commission


def cancel_sell_lot(item_type, price, account_id, operation_type):

    lots = tt_services.market.cmd_cancel_lot(item_type=item_type,
                                             price=price,
                                             owner_id=account_id)

    if not lots:
        return

    cards_logic.change_owner(old_owner_id=accounts_logic.get_system_user_id(),
                             new_owner_id=account_id,
                             operation_type=operation_type,
                             new_storage=cards_relations.STORAGE.FAST,
                             cards_ids=[lot.item_id for lot in lots])
