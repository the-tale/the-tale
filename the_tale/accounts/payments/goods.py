# coding: utf-8

from the_tale.common.postponed_tasks import PostponedTaskPrototype

from the_tale.accounts.payments import postponed_tasks
from the_tale.accounts.payments import exceptions
from the_tale.accounts.payments.logic import transaction_logic
from the_tale.accounts.payments.conf import payments_settings


class PurchaseItem(object):

    def __init__(self, uid, cost, name, description, transaction_description):
        self.uid = uid
        self.cost = int(cost * payments_settings.GLOBAL_COST_MULTIPLIER)
        self.name = name
        self.description = description
        self.transaction_description = transaction_description


    def is_purchasable(self, account, hero):
        return True

    def buy(self, account):
        if account.is_fast:
            raise exceptions.FastAccountError(purchase_uid=self.uid, account_id=account.id)

        self.additional_checks(account)

        transaction = transaction_logic(account=account,
                                        amount=-self.cost,
                                        description=self.transaction_description,
                                        uid='ingame-purchase-<%s>' % self.uid)

        postponed_logic = self.construct_postponed_task(account, transaction)

        postponed_task = PostponedTaskPrototype.create(postponed_logic)
        postponed_task.cmd_wait()

        return postponed_task

    def additional_checks(self, account):
        pass

    def construct_postponed_task(self, account, transaction):
        raise NotImplementedError


class PremiumDays(PurchaseItem):

    def __init__(self, days, **kwargs):
        super(PremiumDays, self).__init__(**kwargs)
        self.days = days

    def construct_postponed_task(self, account, transaction):
        return postponed_tasks.BuyPremium(account_id=account.id, days=self.days, transaction=transaction)


class EnergyCharges(PurchaseItem):

    def __init__(self, charges_number, **kwargs):
        super(EnergyCharges, self).__init__(**kwargs)
        self.charges_number = charges_number

    def construct_postponed_task(self, account, transaction):
        return postponed_tasks.BuyEnergyCharges(account_id=account.id, charges_number=self.charges_number, transaction=transaction)


class ResetHeroPreference(PurchaseItem):

    def __init__(self, preference_type, **kwargs):
        super(ResetHeroPreference, self).__init__(**kwargs)
        self.preference_type = preference_type

    def construct_postponed_task(self, account, transaction):
        return postponed_tasks.BuyResetHeroPreference(account_id=account.id, preference_type=self.preference_type, transaction=transaction)


class ResetHeroAbilities(PurchaseItem):

    def __init__(self, **kwargs):
        super(ResetHeroAbilities, self).__init__(**kwargs)

    def construct_postponed_task(self, account, transaction):
        return postponed_tasks.BuyResetHeroAbilities(account_id=account.id, transaction=transaction)


class RechooseHeroAbilitiesChoices(PurchaseItem):

    def __init__(self, **kwargs):
        super(RechooseHeroAbilitiesChoices, self).__init__(**kwargs)

    def construct_postponed_task(self, account, transaction):
        return postponed_tasks.BuyRechooseHeroAbilitiesChoices(account_id=account.id, transaction=transaction)

    def is_purchasable(self, account, hero):
        return hero.abilities.can_rechoose_abilities_choices()


class PermanentPurchase(PurchaseItem):

    def __init__(self, purchase_type, **kwargs):
        super(PermanentPurchase, self).__init__(**kwargs)
        self.purchase_type = purchase_type

    def additional_checks(self, account):
        if self.purchase_type in account.permanent_purchases:
            raise exceptions.DuplicatePermanentPurchaseError(purchase_uid=self.uid, purchase_type=self.purchase_type, account_id=account.id)

    def construct_postponed_task(self, account, transaction):
        return postponed_tasks.BuyPermanentPurchase(account_id=account.id, purchase_type=self.purchase_type, transaction=transaction)

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
