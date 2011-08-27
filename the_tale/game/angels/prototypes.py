# -*- coding: utf-8 -*-
from django_next.utils.decorators import nested_commit_on_success

from .models import Angel
from ..heroes.prototypes import get_heroes_by_query

def get_angel_by_id(model_id):
    angel = Angel.objects.get(id=model_id)
    return AngelPrototype(model=angel)

def get_angel_by_model(model):
    return AngelPrototype(model=model)

class AngelPrototype(object):

    def __init__(self, model=None):
        self.model = model

    @property
    def id(self): return self.model.id

    @property
    def name(self): return self.model.name

    @property
    def heroes(self): 
        if not hasattr(self, '_heroes'):
            self._heroes = get_heroes_by_query(self.model.heroes.all())
        return self._heroes

    ###########################################
    # Object operations
    ###########################################

    def remove(self): return self.model.delete()
    def save(self): self.model.save(force_update=True)

    def ui_info(self, ignore_actions=False, ignore_quests=False):
        return {'id': self.id,
                'name': self.name
                }

    @classmethod
    @nested_commit_on_success
    def create(cls, account, name):
        angel_model = Angel.objects.create(account=account.model,
                                           name=name)
        return AngelPrototype(model=angel_model)

