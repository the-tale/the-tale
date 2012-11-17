# coding utf-8

from game.models import Bundle, BUNDLE_TYPE

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
        from game.actions.models import Action
        from game.heroes.prototypes import HeroPrototype

        try:
            return cls(Action.objects.filter(hero_id=HeroPrototype.get_by_account_id(account_id).id).select_related().order_by('-order')[0].bundle)
        except IndexError:
            return None

    @property
    def id(self): return self.model.id

    @property
    def type(self): return self.model.type

    def get_owner(self): return self.model.owner
    def set_owner(self, value): self.model.owner = value
    owner = property(get_owner, set_owner)

    @classmethod
    def create(cls):
        bundle = Bundle.objects.create(type=BUNDLE_TYPE.BASIC)
        return BundlePrototype(model=bundle)

    def remove(self):
        self.model.delete() # must delete all members automaticaly

    def save(self):
        self.model.save()

    def __eq__(self, other):
        return self.model == other.model
