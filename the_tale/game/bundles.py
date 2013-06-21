# coding utf-8

from common.utils.prototypes import BasePrototype

from game.models import Bundle, BUNDLE_TYPE


class BundleException(Exception): pass


class BundlePrototype(BasePrototype):
    _model_class = Bundle
    _readonly = ('id', 'type')
    _bidirectional = ('owner', )
    _get_by = ('id',)

    @classmethod
    def distribute(cls, owner):
        cls._model_class.objects.all().update(owner=owner)

    @classmethod
    def get_by_account_id(cls, account_id):
        from game.heroes.prototypes import HeroPrototype
        bundle_id = HeroPrototype.get_by_account_id(account_id).actions.current_action.bundle_id
        return cls.get_by_id(bundle_id)

    def change_owner(self, owner):
        self.owner = owner
        self.save()

    @classmethod
    def create(cls):
        bundle = Bundle.objects.create(type=BUNDLE_TYPE.BASIC)
        return BundlePrototype(model=bundle)

    @classmethod
    def delete_by_id(cls, id_):
        cls._model_class.objects.filter(id=id_).delete()

    def remove(self):
        self._model.delete() # must delete all members automaticaly

    def save(self):
        self._model.save()

    def __eq__(self, other):
        return self._model == other._model
