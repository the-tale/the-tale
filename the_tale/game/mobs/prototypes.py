# -*- coding: utf-8 -*-

import random

from ..heroes.prototypes import BASE_ATTRIBUTES
from ..heroes.habilities import AbilitiesPrototype

from game.balance import formulas as f

class MobException(Exception): pass


class MobPrototype(object):

    def __init__(self, record=None, level=None, health=None, abilities=None):

        self.record = record

        self.level = level

        self.max_health = f.mob_hp_to_lvl(level)
        self.health = self.max_health if health is None else health

        self.abilities = AbilitiesPrototype(abilities=record.abilities) if abilities is None else abilities


    @property
    def level(self): return self.record.level

    @property
    def id(self): return self.record.id

    @property
    def name(self): return self.record.name

    @property
    def normalized_name(self): return self.record.normalized_name

    @property
    def battle_speed(self): return self.record.speed

    @property
    def damage_dispersion(self): return self.record.damage_dispersion

    @property
    def loot(self): return self.record.loot

    @property
    def artifacts(self): return self.record.artifacts


    @property
    def health_percents(self): return float(self.health) / self.max_health

    def get_basic_damage(self):
        return f.expected_damage_to_hero_per_hit(self.level) * (1 + random.uniform(-self.damage_dispersion, self.damage_dispersion))

    def strike_by(self, percents):
        self.health = max(0, self.health - self.max_health * percents)

    def kill(self):
        pass

    def get_loot(self):
        from ..artifacts.storage import ArtifactsDatabase
        return ArtifactsDatabase.storage().generate_loot(self.artifacts, self.loot, self.level)

    def serialize(self):
        return {'level': self.level,
                'id': self.id,
                'health': self.health,
                'abilities': self.abilities.serialize()}

    @classmethod
    def deserialize(cls, storage, data):
        return cls(record=storage.data[data['id']],
                   level=data['level'],
                   health=data['health'],
                   abilities=AbilitiesPrototype.deserialize(data['abilities']))

    def ui_info(self):
        return { 'name': self.name,
                 'health': self.health_percents }
