# coding: utf-8

import math

from the_tale.common.utils.permanent_storage import PermanentRelationsStorage

from the_tale.bank.transaction import Transaction
from the_tale.bank.relations import ENTITY_TYPE, CURRENCY_TYPE

from the_tale.accounts.payments.conf import payments_settings
from the_tale.accounts.payments.relations import PERMANENT_PURCHASE_TYPE


def real_amount_to_game(amount):
    return int(math.ceil(amount * payments_settings.PREMIUM_CURRENCY_FOR_DOLLAR))


def transaction_logic(account, amount, description, uid, force=False):
    return Transaction.create(recipient_type=ENTITY_TYPE.GAME_ACCOUNT,
                              recipient_id=account.id,
                              sender_type=ENTITY_TYPE.GAME_LOGIC,
                              sender_id=0,
                              currency=CURRENCY_TYPE.PREMIUM,
                              amount=amount,
                              description_for_sender=description,
                              description_for_recipient=description,
                              operation_uid=uid,
                              force=force)


def transaction_gm(account, amount, description, game_master):

    return Transaction.create(recipient_type=ENTITY_TYPE.GAME_ACCOUNT,
                              recipient_id=account.id,
                              sender_type=ENTITY_TYPE.GAME_MASTER,
                              sender_id=game_master.id,
                              currency=CURRENCY_TYPE.PREMIUM,
                              amount=amount,
                              description_for_sender=description,
                              description_for_recipient=description,
                              operation_uid='game-master-gift',
                              force=True)



class PermanentRelationsStorage(PermanentRelationsStorage):
    RELATION = PERMANENT_PURCHASE_TYPE
    VALUE_COLUMN = 'value'
