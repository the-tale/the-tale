# coding: utf-8

from common.postponed_tasks import PostponedTaskPrototype

from bank.transaction import Transaction
from bank.relations import ENTITY_TYPE, CURRENCY_TYPE

from accounts.payments.postponed_tasks import BuyPremium
from accounts.payments.exceptions import PayementsError
from accounts.payments.logic import transaction_logic


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

    def buy(self, account):

        if account.is_fast:
            raise PayementsError('try to buy purchase <%s> to fast account %d' % (self.uid, account.id))

        transaction = transaction_logic(account=account,
                                        amount=-self.cost,
                                        description=self.transaction_description,
                                        uid='ingame-purchase-<%s>' % self.uid)

        postponed_logic = BuyPremium(account_id=account.id, days=self.days, transaction=transaction)

        postponed_task = PostponedTaskPrototype.create(postponed_logic)
        postponed_task.cmd_wait()

        return postponed_task
