# coding: utf-8

from common.postponed_tasks import PostponedTaskPrototype

from bank.transaction import Transaction
from bank.relations import ENTITY_TYPE, CURRENCY_TYPE

from accounts.payments.postponed_tasks import BuyPremium


class PurchaseItem(object):

    def __init__(self, uid, cost, name, description, transaction_description):
        self.uid = uid
        self.cost = cost
        self.name = name
        self.description = description
        self.transaction_description = transaction_description


class PremiumDays(PurchaseItem):

    def __init__(self, days, **kwargs):
        super(PremiumDays, self).__init__(**kwargs)
        self.days = days

    def buy(self, account_id):
        transaction = Transaction.create(recipient_type=ENTITY_TYPE.GAME_ACCOUNT,
                                         recipient_id=account_id,
                                         sender_type=ENTITY_TYPE.GAME_LOGIC,
                                         sender_id=0,
                                         currency=CURRENCY_TYPE.PREMIUM,
                                         amount=-self.cost,
                                         description=self.transaction_description)

        postponed_logic = BuyPremium(account_id=account_id, days=self.days, transaction=transaction)

        postponed_task = PostponedTaskPrototype.create(postponed_logic)
        postponed_task.cmd_wait()

        return postponed_task
