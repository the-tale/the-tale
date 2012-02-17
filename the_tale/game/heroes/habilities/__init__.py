# coding: utf-8
import random

from dext.utils import s11n

from .prototypes import ABILITIES, ABILITIES_ACTIVATION_TYPE, ABILITIES_LOGIC_TYPE

__all__ = ['ABILITIES', 'AbilitiesPrototype', 'ABILITIES_LOGIC_TYPE']

class AbilitiesPrototype(object):

    def __init__(self, abilities):
        self.abilities = dict( (ability_id, ABILITIES[ability_id]) for ability_id in abilities)

    @classmethod
    def deserialize(cls, data_string):
        abilities = s11n.from_json(data_string)

        # set default ability, can be removed, when all migrations will be done
        if 'hit' not in abilities:
            abilities.append('hit')

        return cls(abilities=abilities)

    def serialize(self):
        data = self.abilities.keys()
        return s11n.to_json(data)

    @property
    def all(self): return self.abilities.values()

    @property
    def active_abilities(self): return [ability for ability in self.abilities.values() if ability.ACTIVATION_TYPE == ABILITIES_ACTIVATION_TYPE.ACTIVE]

    @property
    def passive_abilities(self): return [ability for ability in self.abilities.values() if ability.ACTIVATION_TYPE == ABILITIES_ACTIVATION_TYPE.PASSIVE]

    def has(self, ability_id): return ability_id in self.abilities

    def get(self, ability_id): return self.abilities[ability_id]

    def add(self, ability_id): 
        self.abilities[ability_id] = ABILITIES[ability_id]


    def get_for_choose(self, hero):
        
        random.seed(hero.id * (hero.destiny_points_spend + 1))

        MAX_ABILITIES = 4

        candidates = []
        for ability_key, ability in ABILITIES.items():
            if ability_key in self.abilities:
                continue
            candidates.append(ability_key)
        choices = random.sample(candidates, min(MAX_ABILITIES, len(candidates)))

        result = []

        for choice in choices:
            result.append(ABILITIES[choice])

        return result
