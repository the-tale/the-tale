# coding utf-8

from game.models import Bundle, BundleMember, BUNDLE_TYPE

class BundleException(Exception): pass

class BundlePrototype(object):

    def __init__(self, model):
        self.model = model

    @classmethod
    def get_by_id(cls, model_id):
        try:
            return cls(model=Bundle.objects.get(id=model_id))
        except Bundle.DoesNotExist:
            return None

    @classmethod
    def get_by_account_id(cls, account_id):
        try:
            return cls(BundleMember.objects.select_related().get(account_id=account_id).bundle)
        except BundleMember.DoesNotExist:
            return None

    @property
    def id(self): return self.model.id

    @property
    def type(self): return self.model.type

    def get_owner(self): return self.model.owner
    def set_owner(self, value): self.model.owner = value
    owner = property(get_owner, set_owner)

    @property
    def is_single(self):
        if not hasattr(self, '_is_single'):
            self._is_single = self.model.members.all().count()
        return self._is_single

    @classmethod
    def create(cls, account):

        bundle = Bundle.objects.create(type=BUNDLE_TYPE.BASIC)
        BundleMember.objects.create(account=account.model, bundle=bundle)

        return BundlePrototype(model=bundle)

    def remove(self):
        self.model.delete() # must delete all members automaticaly

    def save(self):
        self.model.save()

    def get_accounts_ids(self):
        return BundleMember.objects.filter(bundle_id=self.id).values_list('account_id', flat=True)

    ##########################
    # methods for test purposes

    # DEPRECATED

    # def tests_get_last_action(self):
    #     return self.actions[sorted(self.actions.keys())[-1]]

    # def tests_get_hero(self):
    #     return self.heroes.values()[0]

    def __eq__(self, other):
        return self.model == other.model
