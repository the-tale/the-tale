
import smart_imports

smart_imports.all()

PURCHAGE_UID = 'ingame-purchase-<{}>'


class PurchaseItem(object):

    def __init__(self, uid, cost, name, description, transaction_description, full_name=None, tooltip=None):
        self.uid = uid
        self.cost = cost
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

        transaction = logic.transaction_logic(account=account,
                                              amount=-self.cost,
                                              description=self.transaction_description,
                                              uid=PURCHAGE_UID.format(self.uid))

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
