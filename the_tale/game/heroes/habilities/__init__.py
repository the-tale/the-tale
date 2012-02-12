# coding: utf-8
import random

from dext.utils import s11n

from .prototypes import ABILITIES, ABILITIES_EVENTS

__all__ = ['ABILITIES', 'ABILITIES_EVENTS', 'HeroAbilitiesPrototype']

class HeroAbilitiesPrototype(object):

    def __init__(self, abilities):
        self.abilities = abilities

    @classmethod
    def deserialize(cls, data_string):
        data = s11n.from_json(data_string)
        abilities = {}
        for ability_id, ability_level in data.items():
            abilities[ability_id] = ABILITIES[ability_id](ability_level)
        return cls(abilities=abilities)

    @property
    def all(self): return self.abilities.values()

    def has(self, ability_id): return ability_id in self.abilities

    def get(self, ability_id): return self.abilities[ability_id]

    def add(self, ability_id): 
        self.abilities[ability_id] = ABILITIES[ability_id](0)

    def serialize(self):
        data = dict( (ability_id, ability.level) for ability_id, ability in self.abilities.items() )
        return s11n.to_json(data)


    def get_next_level_for(self, ability_id):

        if ability_id in self.abilities:
            ability = self.abilities[ability_id]
            if ability.has_max_level:
                return None
            return ability.level + 1

        return 0


    def get_for_choose(self, hero):
        
        random.seed(hero.id * (hero.destiny_points_spend + 1))

        MAX_ABILITIES = 8
        HERO_ABILITIES = 4

        exists_candidates = []
        for ability_key, ability in self.abilities.items():
            if ability.has_max_level:
                continue
            exists_candidates.append(ability_key)
        
        exists_choices = random.sample(exists_candidates, min(HERO_ABILITIES, len(exists_candidates)))

        new_candidates = []
        for ability_key, ability in ABILITIES.items():
            if ability_key in self.abilities:
                continue
            new_candidates.append(ability_key)
        new_choices = random.sample(new_candidates, min(MAX_ABILITIES - HERO_ABILITIES, len(new_candidates)))

        choices = exists_choices + new_choices

        result = []

        for choice in choices:
            level = 0
            if choice in self.abilities:
                level = self.abilities[choice].level + 1
            result.append(ABILITIES[choice](level))

        return result

    def trigger(self, hero, event_type):
        expected_abilities = []

        for ability_id, ability in self.abilities.items():
            if event_type in ability.EVENTS:
                if ability.can_use(hero):
                    expected_abilities.append(ability)

        priority_domain = sum([ability.priority for ability in expected_abilities])

        if priority_domain==0:
            return 

        choice = random.randint(0, priority_domain-1)

        choosen_ability = None

        for ability in expected_abilities:
            choice -= ability.priority
            if choice <= 0:
                choosen_ability = ability
                break

        if choosen_ability is None:
            return

        choosen_ability.use(hero)


