# coding: utf-8

from the_tale.common.postponed_tasks import PostponedTaskPrototype

from the_tale.accounts.payments import postponed_tasks
from the_tale.accounts.payments import exceptions
from the_tale.accounts.payments.logic import transaction_logic


class PurchaseItem(object):

    def __init__(self, uid, cost, name, description, transaction_description):
        self.uid = uid
        self.cost = cost
        self.name = name
        self.description = description
        self.transaction_description = transaction_description


    def is_purchasable(self, account, hero):
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

        postponed_logic = postponed_tasks.BuyPremium(account_id=account.id, days=self.days, transaction=transaction)

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

        postponed_logic = postponed_tasks.BuyEnergyCharges(account_id=account.id, charges_number=self.charges_number, transaction=transaction)

        postponed_task = PostponedTaskPrototype.create(postponed_logic)
        postponed_task.cmd_wait()

        return postponed_task


class ResetHeroPreference(PurchaseItem):

    def __init__(self, preference_type, **kwargs):
        super(ResetHeroPreference, self).__init__(**kwargs)
        self.preference_type = preference_type

    def buy(self, account):

        if account.is_fast:
            raise exceptions.FastAccountError(purchase_uid=self.uid, account_id=account.id)

        transaction = transaction_logic(account=account,
                                        amount=-self.cost,
                                        description=self.transaction_description,
                                        uid='ingame-purchase-<%s>' % self.uid)

        postponed_logic = postponed_tasks.BuyResetHeroPreference(account_id=account.id, preference_type=self.preference_type, transaction=transaction)

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

        postponed_logic = postponed_tasks.BuyPermanentPurchase(account_id=account.id, purchase_type=self.purchase_type, transaction=transaction)

        postponed_task = PostponedTaskPrototype.create(postponed_logic)
        postponed_task.cmd_wait()

        return postponed_task


    def is_purchasable(self, account, hero):

        if self.purchase_type in account.permanent_purchases:
            return False

        if self.purchase_type.might_required is not None:
            if account.might >= self.purchase_type.might_required:
                return False

        if self.purchase_type.level_required is not None:
            if hero.level >= self.purchase_type.level_required:
                return False

        return True
