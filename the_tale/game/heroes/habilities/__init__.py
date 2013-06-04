# coding: utf-8
import copy
import random

from game.heroes.habilities.prototypes import ABILITY_TYPE, ABILITY_AVAILABILITY, ABILITY_ACTIVATION_TYPE, ABILITY_LOGIC_TYPE

from game.heroes.habilities.battle import ABILITIES as BATTLE_ABILITIES
from game.heroes.habilities.attributes import ABILITIES as ATTRIBUTES_ABILITIES
from game.heroes.habilities.modifiers import ABILITIES as MODIFIERS_ABILITIES
from game.heroes.habilities.nonbattle import ABILITIES as NONBATTLE_ABILITIES


ABILITIES = dict(**BATTLE_ABILITIES)
ABILITIES.update(**ATTRIBUTES_ABILITIES)
ABILITIES.update(**MODIFIERS_ABILITIES)
ABILITIES.update(**NONBATTLE_ABILITIES)

__all__ = ['ABILITIES', 'ABILITY_LOGIC_TYPE', 'ABILITY_TYPE', 'ABILITY_AVAILABILITY', 'ABILITY_ACTIVATION_TYPE']

class AbilitiesPrototype(object):

    def __init__(self):
        self.abilities = {}
        self.updated = False

    def serialize(self):
        data = {'abilities': {}}
        for ability_id, ability in self.abilities.items():
            data['abilities'][ability_id] = ability.serialize()
        return data

    @classmethod
    def deserialize(cls, data):
        abilities = cls()

        for ability_id, ability_data in data['abilities'].items():
            ability = ABILITIES[ability_id].deserialize(ability_data)
            abilities.abilities[ability_id] = ability

        return abilities

    @classmethod
    def create(cls):
        abilities = cls()
        ability = ABILITIES['hit'](level=1)
        abilities.abilities[ability.get_id()] = ability
        return abilities

    @property
    def all(self): return self.abilities.values()

    @property
    def active_abilities(self): return [ability for ability in self.abilities.values() if ability.activation_type.is_active]

    @property
    def passive_abilities(self): return [ability for ability in self.abilities.values() if ability.activation_type.is_passive]

    def has(self, ability_id): return ability_id in self.abilities

    def get(self, ability_id): return self.abilities[ability_id]

    def add(self, ability_id, level=1):
        self.updated = True
        self.abilities[ability_id] = ABILITIES[ability_id](level=level)

    def increment_level(self, ability_id):
        self.updated = True
        self.abilities[ability_id].level += 1


    def get_candidates(self, ability_type, max_active_abilities, max_passive_abilities):

        # filter by type (battle, nonbattle, etc...)
        ability_classes = filter(lambda a: a.TYPE==ability_type, ABILITIES.values())
        choosen_abilities = filter(lambda a: a.TYPE==ability_type, self.abilities.values())

        # filter by availability for players
        ability_classes = filter(lambda a: a.AVAILABILITY & ABILITY_AVAILABILITY.FOR_PLAYERS, ability_classes)

        # filter abilities with max level
        ability_classes = filter(lambda a: not (self.has(a.get_id()) and self.get(a.get_id()).has_max_level), ability_classes)

        # filter unchoosen abilities if there are no free slots
        free_active_slots = max_active_abilities - len(filter(lambda a: a.ACTIVATION_TYPE==ABILITY_ACTIVATION_TYPE.ACTIVE, choosen_abilities))
        free_passive_slots = max_passive_abilities - len(filter(lambda a: a.ACTIVATION_TYPE==ABILITY_ACTIVATION_TYPE.PASSIVE, choosen_abilities))

        candidates = [a(level=1 if not self.has(a.get_id()) else self.get(a.get_id()).level+1)
                      for a in ability_classes]

        if free_active_slots <= 0:
            candidates = filter(lambda a: not a.activation_type.is_active or self.has(a.get_id()), candidates)

        if free_passive_slots <= 0:
            candidates = filter(lambda a: not a.activation_type.is_passive or self.has(a.get_id()), candidates)

        return candidates


    def get_for_choose(self, candidates, max_old_abilities_for_choose, max_abilities_for_choose):
        old_candidates = filter(lambda a: self.has(a.get_id()), candidates)
        new_candidates = filter(lambda a: not self.has(a.get_id()), candidates)

        first_old_candidates = random.sample(old_candidates, min(max_old_abilities_for_choose, len(old_candidates)))
        # second_old_candidates = filter(lambda a: a not in first_old_candidates, old_candidates)
        new_candidates = random.sample(new_candidates, min(max_abilities_for_choose - len(first_old_candidates), len(new_candidates)))

        candidates = first_old_candidates + new_candidates

        # if len(candidates) < max_abilities_for_choose:
        #     candidates += random.sample(filter(lambda a: a not in candidates, second_old_candidates),
        #                                 min(len(second_old_candidates), max_abilities_for_choose - len(candidates)))

        random.shuffle(candidates)

        return candidates

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

    def update_items_of_expenditure_priorities(self, hero, priorities):
        priorities = copy.deepcopy(priorities)
        for ability in self.abilities.values():
            priorities = ability.update_items_of_expenditure_priorities(hero, priorities)
        return priorities

    def can_get_artifact_for_quest(self, hero):
        for ability in self.abilities.values():
            if ability.can_get_artifact_for_quest(hero):
                return True
        return False

    def can_buy_better_artifact(self, hero):
        for ability in self.abilities.values():
            if ability.can_buy_better_artifact(hero):
                return True
        return False

    def randomized_level_up(self, levels):

        for i in xrange(levels):

            candidates = []

            for ability in self.abilities.values():
                if not ability.has_max_level:
                    candidates.append(ability)

            if not candidates: return levels - i

            ability = random.choice(candidates)
            ability.level += 1
            self.updated = True

        return 0


    def __eq__(self, other):
        return set(self.abilities.keys()) == set(other.abilities.keys())
