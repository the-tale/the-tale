# coding: utf-8
import random
import copy

from game.heroes.habilities.prototypes import ABILITIES_ACTIVATION_TYPE, ABILITIES_LOGIC_TYPE

from game.heroes.habilities.prototypes import ABILITIES as COMMON_ABILITIES
from game.heroes.habilities.attributes import ABILITIES as ATTRIBUTES_ABILITIES
from game.heroes.habilities.nonbattle import ABILITIES as NONBATTLE_ABILITIES

ABILITIES = dict(COMMON_ABILITIES)
ABILITIES.update(**ATTRIBUTES_ABILITIES)
ABILITIES.update(**NONBATTLE_ABILITIES)

__all__ = ['ABILITIES', 'AbilitiesPrototype', 'ABILITIES_LOGIC_TYPE']

class AbilitiesPrototype(object):

    def __init__(self, abilities):
        self.abilities = dict( (ability_id, ABILITIES[ability_id]) for ability_id in abilities)
        self.updated = True

    @classmethod
    def deserialize(cls, data):
        abilities = copy.deepcopy(data)

        # set default ability, can be removed, when all migrations will be done
        if 'hit' not in abilities:
            abilities.append('hit')

        return cls(abilities=abilities)

    def serialize(self):
        return self.abilities.keys()

    @property
    def all(self): return self.abilities.values()

    @property
    def active_abilities(self): return [ability for ability in self.abilities.values() if ability.ACTIVATION_TYPE == ABILITIES_ACTIVATION_TYPE.ACTIVE]

    @property
    def passive_abilities(self): return [ability for ability in self.abilities.values() if ability.ACTIVATION_TYPE == ABILITIES_ACTIVATION_TYPE.PASSIVE]

    def has(self, ability_id): return ability_id in self.abilities

    def get(self, ability_id): return self.abilities[ability_id]

    def add(self, ability_id):
        self.updated = True
        self.abilities[ability_id] = ABILITIES[ability_id]


    def get_for_choose(self, hero):

        random.seed(hero.id * (hero.destiny_points_spend + 1))

        MAX_ABILITIES = 4

        candidates = []
        for ability_key, ability in ABILITIES.items():
            if ability_key in self.abilities:
                continue
            if not ability.AVAILABLE_TO_PLAYERS:
                continue
            candidates.append(ability_key)
        choices = random.sample(candidates, min(MAX_ABILITIES, len(candidates)))

        result = []

        for choice in choices:
            result.append(ABILITIES[choice])

        return result

    def modify_attribute(self, name, value):
        for ability in self.abilities.values():
            value = ability.modify_attribute(name, value)
        return value

    def update_context(self, actor, enemy):
        for ability in self.abilities.values():
            ability.update_context(actor, enemy)

    def update_quest_reward(self, hero, money):
        for ability in self.abilities.values():
            money = ability.update_quest_reward(hero, money)
        return money

    def update_buy_price(self, hero, money):
        for ability in self.abilities.values():
            money = ability.update_buy_price(hero, money)
        return money

    def update_sell_price(self, hero, money):
        for ability in self.abilities.values():
            money = ability.update_sell_price(hero, money)
        return money

    def __eq__(self, other):
        return set(self.abilities.keys()) == set(other.abilities.keys())
