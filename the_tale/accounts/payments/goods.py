# coding: utf-8

from the_tale.common.postponed_tasks import PostponedTaskPrototype

from the_tale.accounts.payments import postponed_tasks
from the_tale.accounts.payments import exceptions
from the_tale.accounts.payments.logic import transaction_logic
from the_tale.accounts.payments.conf import payments_settings


class PurchaseGroup(object):

    def __init__(self, type, name, description, items, short_name=None):
        self.type = type
        self.name = name
        self.short_name = short_name if short_name is not None else self.name
        self.description = description
        self.items = items

    @property
    def uid(self): return self.type.uid

    def items_table(self, columns):
        table = []

        for i in xrange(0, len(self.items), columns):
            table.append(self.items[i:i+columns])

        while len(table[-1]) != columns:
            table[-1].append(None)

        return table


class PurchaseItem(object):

    def __init__(self, uid, cost, name, description, transaction_description, full_name=None, tooltip=None):
        self.uid = uid
        self.cost = int(cost * payments_settings.GLOBAL_COST_MULTIPLIER)
        self.name = name
        self.full_name = full_name if full_name is not None else name
        self.description = description
        self.transaction_description = transaction_description
        self.tooltip = tooltip


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

    def is_purchasable(self, account, hero):
        return not account.is_premium_infinit


class Energy(PurchaseItem):

    def __init__(self, energy, **kwargs):
        super(Energy, self).__init__(**kwargs)
        self.energy = energy

    def construct_postponed_task(self, account, transaction):
        return postponed_tasks.BuyEnergy(account_id=account.id, energy=self.energy, transaction=transaction)


class ChangeHeroHabits(PurchaseItem):

    def __init__(self, habit_type, habit_value, **kwargs):
        super(ChangeHeroHabits, self).__init__(**kwargs)
        self.habit_type = habit_type
        self.habit_value = habit_value

    def construct_postponed_task(self, account, transaction):
        return postponed_tasks.BuyChangeHeroHabits(account_id=account.id, habit_type=self.habit_type, habit_value=self.habit_value, transaction=transaction)


class ResetHeroAbilities(PurchaseItem):

    def __init__(self, **kwargs):
        super(ResetHeroAbilities, self).__init__(**kwargs)

    def construct_postponed_task(self, account, transaction):
        return postponed_tasks.BuyResetHeroAbilities(account_id=account.id, transaction=transaction)


class RandomPremiumChest(PurchaseItem):

    def __init__(self, **kwargs):
        super(RandomPremiumChest, self).__init__(**kwargs)

    def construct_postponed_task(self, account, transaction):
        return postponed_tasks.BuyRandomPremiumChest(account_id=account.id, transaction=transaction)


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



class Cards(PurchaseItem):

    def __init__(self, card_type, count, **kwargs):
        super(Cards, self).__init__(**kwargs)
        self.card_type = card_type
        self.count = count

    def construct_postponed_task(self, account, transaction):
        return postponed_tasks.BuyCards(account_id=account.id, card_type=self.card_type, count=self.count, transaction=transaction)
