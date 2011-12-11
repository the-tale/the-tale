# -*- coding: utf-8 -*-
from django_next.utils import s11n
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

    def heroes(self): 
        #TODO: now this code only works on bundle init phase
        #      using it from another places is dangerouse becouse of 
        #      desinchronization between workers and database
        if not hasattr(self, '_heroes'):
            self._heroes = get_heroes_by_query(self.model.heroes.all())
        return self._heroes

    def load_abilities(self):
        from ..abilities.prototypes import AbilityPrototype
        data = s11n.from_json(self.model.abilities)
        abilities = {}
        for ability_dict in data.values():
            ability = AbilityPrototype.deserialize(ability_dict)
            abilities[ability.get_type()] = ability
        self._abilities = abilities

    def save_abilities(self):
        data = {}
        for ability in self.abilities.values():
            data[ability.get_type()] = ability.serialize()
        self.model.abilities = s11n.to_json(data)

    @property
    def abilities(self):
        if not hasattr(self, '_abilities'):
            self.load_abilities()
        return self._abilities

    ###########################################
    # Object operations
    ###########################################

    def remove(self): return self.model.delete()
    def save(self): 
        self.save_abilities()
        self.model.save(force_update=True)

    def ui_info(self, ignore_actions=False, ignore_quests=False):
        return {'id': self.id,
                'name': self.name,
                'energy': { 'max': self.energy_maximum,
                            'regen': self.energy_regeneration,
                            'value': self.energy },
                'abilities': [ability.ui_info() for ability_type, ability in self.abilities.items()]
                }

    @classmethod
    @nested_commit_on_success
    def create(cls, account, name):
        from ..abilities import deck
        # TODO: rewrite from create-change-save to save
        angel_model = Angel.objects.create(account=account.model, name=name)
        angel = AngelPrototype(model=angel_model)
        angel.abilities.update({deck.HealHero.get_type(): deck.HealHero()})
        angel.save()

        return angel


    ###########################################
    # Next turn operations
    ###########################################

    def process_turn(self, turn_number):
        self.energy += self.energy_regeneration
        if self.energy > self.energy_maximum:
            self.energy = self.energy_maximum

        return turn_number + 1


