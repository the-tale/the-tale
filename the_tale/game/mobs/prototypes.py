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

    HEALTH_RELATIVE_TO_HERO = None
    BATTLE_SPEED = None
    POWER_PER_LEVEL = None
    DAMAGE_DISPERSION = None

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

    def get_basic_damage(self):
        return self.power * (1 + random.uniform(-self.DAMAGE_DISPERSION, self.DAMAGE_DISPERSION))

    @classmethod
    def get_type_name(cls):
        return cls.__name__.lower()

    def strike_by(self, percents):
        self.health = max(0, self.health - self.max_health * percents)

    def kill(self):
        pass

    def get_loot(self):
        from ..artifacts.constructors import ArtifactConstructorPrototype
        return ArtifactConstructorPrototype.generate_loot(self.LOOT_LIST, self.level)

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
    DAMAGE_DISPERSION = 0.15
    ABILITIES = ['hit', 'regeneration']

    LOOT_LIST = [ (10, 'useless_rat_tail'),
                  (1, 'useless_piece_of_cheese') ]


class Bandit(MobPrototype):

    NAME = u'бандит'

    HEALTH_RELATIVE_TO_HERO = 0.7
    BATTLE_SPEED = 4
    POWER_PER_LEVEL = 2
    DAMAGE_DISPERSION = 0.3
    ABILITIES = ['hit']

    LOOT_LIST = [ (1, 'useless_fake_amulet'),
                  (1, 'weapon_broken_sword'),
                  (1, 'armor_decrepit_plate')]
                  


MOB_PROTOTYPES = dict( (type_name.lower(), prototype)
                       for type_name, prototype in globals().items()
                       if isinstance(prototype, type) and issubclass(prototype, MobPrototype) and prototype != MobPrototype)

def get_random_mob(hero):
    prototype = random.choice(MOB_PROTOTYPES.values())
    return prototype(hero.level)
                                 
                                 
