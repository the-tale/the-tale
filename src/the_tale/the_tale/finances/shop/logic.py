import math

from dext.common.utils.urls import url

from the_tale.common.utils.permanent_storage import PermanentRelationsStorage

from the_tale.game.cards import logic as cards_logic

from the_tale.finances.bank import transaction as bank_transaction
from the_tale.finances.bank import prototypes as bank_prototypes
from the_tale.finances.bank import relations as bank_relations

from the_tale.finances.shop.conf import payments_settings
from the_tale.finances.shop.relations import PERMANENT_PURCHASE_TYPE

from . import conf


def create_sell_lot_url():
    return url('shop:create-sell-lot')


def close_sell_lot_url():
    return url('shop:close-sell-lot')


def cancel_sell_lot_url():
    return url('shop:cancel-sell-lot')


def info_url():
    return url('shop:info')


def item_type_prices_url():
    return url('shop:item-type-prices')


def real_amount_to_game(amount):
    return int(math.ceil(amount * payments_settings.PREMIUM_CURRENCY_FOR_DOLLAR))


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



class PermanentRelationsStorage(PermanentRelationsStorage):
    RELATION = PERMANENT_PURCHASE_TYPE
    VALUE_COLUMN = 'value'


def close_lot(item_type, price, buyer_id):
    from . import postponed_tasks

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

def get_commission(price):
    commission = int(math.floor(price*conf.payments_settings.MARKET_COMISSION))

    if commission == 0:
        commission = 1

    return commission
