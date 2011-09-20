# -*- coding: utf-8 -*-
from django_next.utils.decorators import nested_commit_on_success

from ..heroes.prototypes import get_heroes_by_query

from .models import Angel
from .game_info import ENERGY

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
    def energy_maximum(self): return ENERGY.MAXIMUM

    @property
    def energy_regeneration(self): return ENERGY.REGENERATION

    def get_energy(self): return self.model.energy
    def set_energy(self, value): self.model.energy = value
    energy = property(get_energy, set_energy)

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
                'name': self.name,
                'energy': { 'max': self.energy_maximum,
                            'regen': self.energy_regeneration,
                            'value': self.energy }
                }

    @classmethod
    @nested_commit_on_success
    def create(cls, account, name):
        angel_model = Angel.objects.create(account=account.model,
                                           name=name)
        return AngelPrototype(model=angel_model)


    ###########################################
    # Next turn operations
    ###########################################

    def next_turn_pre_update(self, turn):
        self.energy += self.energy_regeneration
        if self.energy > self.energy_maximum:
            self.energy = self.energy_maximum


