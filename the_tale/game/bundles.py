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
    def get_by_account_id(cls, account_id):
        from game.heroes.prototypes import HeroPrototype

        try:
            return cls(Action.objects.filter(hero_id=HeroPrototype.get_by_account_id(account_id).id).select_related().order_by('-order')[0].bundle)
        except IndexError:
            return None

    @classmethod
    def create(cls):
        bundle = Bundle.objects.create(type=BUNDLE_TYPE.BASIC)
        return BundlePrototype(model=bundle)

    @classmethod
    def remove_unused_bundles(cls):
        from django.db import models
        Bundle.objects.annotate(actions_number=models.Count('action')).filter(actions_number=0).delete()

    def remove(self):
        self._model.delete() # must delete all members automaticaly

    def save(self):
        self._model.save()

    def __eq__(self, other):
        return self._model == other._model
