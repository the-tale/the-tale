# -*- coding: utf-8 -*-

import random

from dext.utils import s11n

from ..heroes.prototypes import BASE_ATTRIBUTES
from ..heroes.habilities import AbilitiesPrototype
from ..artifacts import constructors as loot

def get_mob_by_data(data):
    return MOB_PROTOTYPES[data['type']](data=data)

class MobException(Exception): pass


class MobPrototype(object):

    NAME = ''
    LOOT_LIST = []

    LOOT_BASIC_MODIFICATOR = None
    LOOT_EFFECTS_MODIFICATOR = None

    HEALTH_RELATIVE_TO_HERO = None
    BATTLE_SPEED = None
    POWER_PER_LEVEL = None

    ABILITIES = []

    def __init__(self, level, health=None):
        self.level = level
        self.health = health if health else self.max_health
        self.power = self.POWER_PER_LEVEL * level
        self.battle_speed = self.BATTLE_SPEED
        
        self.abilities = AbilitiesPrototype(abilities=self.ABILITIES)

    @property
    def name(self):
        return self.NAME

    @property
    def max_health(self):
        return int(BASE_ATTRIBUTES.get_max_health(self.level) * self.HEALTH_RELATIVE_TO_HERO)

    @property
    def health_percents(self): return float(self.health) / self.max_health

    @classmethod
    def get_type_name(cls):
        return cls.__name__.lower()

    def strike_by(self, percents):
        self.health = max(0, self.health - self.max_health * percents)

    def kill(self):
        pass

    def get_loot(self):
        from ..artifacts.constructors import generate_loot
        return generate_loot(self.LOOT_LIST, self.level, self.LOOT_BASIC_MODIFICATOR)

    def serialize(self):
        return s11n.to_json({'type': self.get_type_name(),
                             'level': self.level,
                             'health': self.health})

    @classmethod
    def deserialize(cls, data_string):
        data = s11n.from_json(data_string)
        if not data:
            return None
        return MOB_PROTOTYPES[data['type']](level=data.get('level', 1),
                                            health=data.get('health', 0))


    def ui_info(self):
        return { 'name': self.name,
                 'health': self.health_percents }



class Rat(MobPrototype):

    NAME = u'крыса'

    HEALTH_RELATIVE_TO_HERO = 0.3
    BATTLE_SPEED = 6
    POWER_PER_LEVEL = 1
    ABILITIES = ['hit', 'regeneration']

    LOOT_LIST = [ (10, loot.RatTailConstructor),
                  (1, loot.PieceOfCheeseConstructor) ]
    LOOT_BASIC_MODIFICATOR = 0.5


class Bandit(MobPrototype):

    NAME = u'бандит'

    HEALTH_RELATIVE_TO_HERO = 0.7
    BATTLE_SPEED = 4
    POWER_PER_LEVEL = 2
    ABILITIES = ['hit']

    LOOT_LIST = [ (1, loot.FakeAmuletConstructor),
                  (1, loot.BrokenSword),
                  (1, loot.DecrepitPlate)]
                  
    LOOT_BASIC_MODIFICATOR = 1.0


MOB_PROTOTYPES = dict( (type_name.lower(), prototype)
                       for type_name, prototype in globals().items()
                       if isinstance(prototype, type) and issubclass(prototype, MobPrototype) and prototype != MobPrototype)

def get_random_mob(hero):
    prototype = random.choice(MOB_PROTOTYPES.values())
    return prototype(hero.level)
                                 
                                 
