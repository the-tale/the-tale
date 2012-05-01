# -*- coding: utf-8 -*-
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
    def id(self): return self.record.id

    @property
    def name(self): return self.record.name

    @property
    def normalized_name(self): return (self.record.normalized_name, self.record.morph)

    @property
    def initiative(self): return self.record.speed

    @property
    def loot(self): return self.record.loot

    @property
    def artifacts(self): return self.record.artifacts

    @property
    def health_percents(self): return float(self.health) / self.max_health

    @property
    def damage(self): return self.record.damage

    @property
    def basic_damage(self): return f.expected_damage_to_hero_per_hit(self.level) * self.damage

    def strike_by(self, percents):
        self.health = max(0, self.health - self.max_health * percents)

    def kill(self):
        pass

    def get_loot(self):
        from ..artifacts.storage import ArtifactsDatabase
        return ArtifactsDatabase.storage().generate_loot(self.artifacts, self.loot, artifact_level=self.level, loot_level=self.record.level)

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
