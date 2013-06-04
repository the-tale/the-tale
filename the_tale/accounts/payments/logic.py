# coding: utf-8

import math

from bank.transaction import Transaction
from bank.relations import ENTITY_TYPE, CURRENCY_TYPE

from accounts.payments.conf import payments_settings

def real_amount_to_game(amount):
    return int(math.ceil(amount * payments_settings.PREMIUM_CURRENCY_FOR_DOLLAR))


def transaction_logic(account, amount, description, uid):
    return Transaction.create(recipient_type=ENTITY_TYPE.GAME_ACCOUNT,
                              recipient_id=account.id,
                              sender_type=ENTITY_TYPE.GAME_LOGIC,
                              sender_id=0,
                              currency=CURRENCY_TYPE.PREMIUM,
                              amount=amount,
                              description=description,
                              operation_uid=uid)


def transaction_gm(account, amount, description, game_master):

    return Transaction.create(recipient_type=ENTITY_TYPE.GAME_ACCOUNT,
                              recipient_id=account.id,
                              sender_type=ENTITY_TYPE.GAME_MASTER,
                              sender_id=game_master.id,
                              currency=CURRENCY_TYPE.PREMIUM,
                              amount=amount,
                              description=description,
                              operation_uid='game-master-gift',
                              force=True)
