# coding: utf-8

from common.postponed_tasks import PostponedTaskPrototype

from accounts.payments.postponed_tasks import BuyPremium, BuyPermanentPurchase, BuyEnergyCharges
from accounts.payments import exceptions
from accounts.payments.logic import transaction_logic
from accounts.clans.conf import clans_settings


class PurchaseItem(object):

    def __init__(self, uid, cost, name, description, transaction_description):
        self.uid = uid
        self.cost = cost
        self.name = name
        self.description = description
        self.transaction_description = transaction_description


    def is_purchasable(self, account):
        return True


class PremiumDays(PurchaseItem):

    def __init__(self, days, **kwargs):
        super(PremiumDays, self).__init__(**kwargs)
        self.days = days

    def buy(self, account):

        if account.is_fast:
            raise exceptions.FastAccountError(purchase_uid=self.uid, account_id=account.id)

        transaction = transaction_logic(account=account,
                                        amount=-self.cost,
                                        description=self.transaction_description,
                                        uid='ingame-purchase-<%s>' % self.uid)

        postponed_logic = BuyPremium(account_id=account.id, days=self.days, transaction=transaction)

        postponed_task = PostponedTaskPrototype.create(postponed_logic)
        postponed_task.cmd_wait()

        return postponed_task


class EnergyCharges(PurchaseItem):

    def __init__(self, charges_number, **kwargs):
        super(EnergyCharges, self).__init__(**kwargs)
        self.charges_number = charges_number

    def buy(self, account):

        if account.is_fast:
            raise exceptions.FastAccountError(purchase_uid=self.uid, account_id=account.id)

        transaction = transaction_logic(account=account,
                                        amount=-self.cost,
                                        description=self.transaction_description,
                                        uid='ingame-purchase-<%s>' % self.uid)

        postponed_logic = BuyEnergyCharges(account_id=account.id, charges_number=self.charges_number, transaction=transaction)

        postponed_task = PostponedTaskPrototype.create(postponed_logic)
        postponed_task.cmd_wait()

        return postponed_task


class PermanentPurchase(PurchaseItem):

    def __init__(self, purchase_type, **kwargs):
        super(PermanentPurchase, self).__init__(**kwargs)
        self.purchase_type = purchase_type

    def buy(self, account):

        if account.is_fast:
            raise exceptions.FastAccountError(purchase_uid=self.uid, account_id=account.id)

        if self.purchase_type in account.permanent_purchases:
            raise exceptions.DuplicatePermanentPurchaseError(purchase_uid=self.uid, purchase_type=self.purchase_type, account_id=account.id)

        transaction = transaction_logic(account=account,
                                        amount=-self.cost,
                                        description=self.transaction_description,
                                        uid='ingame-purchase-<%s>' % self.uid)

        postponed_logic = BuyPermanentPurchase(account_id=account.id, purchase_type=self.purchase_type, transaction=transaction)

        postponed_task = PostponedTaskPrototype.create(postponed_logic)
        postponed_task.cmd_wait()

        return postponed_task


    def is_purchasable(self, account):

        if self.purchase_type in account.permanent_purchases:
            return False

        if self.purchase_type._is_CLAN_OWNERSHIP_RIGHT:
            if account.might >= clans_settings.OWNER_MIGHT_REQUIRED:
                return False

        return True
