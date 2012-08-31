# -*- coding: utf-8 -*-
import random

from game.balance import constants as c, formulas as f

from game.artifacts.conf import EQUIP_TYPE, RARITY_TYPE
from game.artifacts.exceptions import ArtifactsException


class ArtifactPrototype(object):

    def __init__(self, record=None, power=None, quest=False, quest_uuid=None, bag_uuid=None, level=0):
        self.record = record
        self.quest = quest
        self.power = power
        self.level = level

        self.quest_uuid = quest_uuid
        self.bag_uuid = bag_uuid


    @property
    def id(self): return self.record.id

    @property
    def type(self): return self.record.type

    @property
    def rarity(self): return self.record.rarity

    @property
    def equip_type(self): return self.record.slot

    @property
    def name(self): return self.record.name

    @property
    def normalized_name(self): return (self.record.normalized_name, self.record.morph)

    @property
    def min_lvl(self): return self.record.min_lvl

    @property
    def max_lvl(self): return self.record.max_lvl

    @property
    def is_useless(self): return self.record.is_useless

    @property
    def can_be_equipped(self):
        from game.heroes.bag import ARTIFACT_TYPES_TO_SLOTS
        return self.equip_type in ARTIFACT_TYPES_TO_SLOTS

    def set_quest_uuid(self, uuid): self.quest_uuid = uuid

    def set_bag_uuid(self, uuid): self.bag_uuid = uuid

    def get_sell_price(self):

        multiplier = 1+random.uniform(-c.PRICE_DELTA, c.PRICE_DELTA)

        if self.is_useless:
            if self.rarity == RARITY_TYPE.NORMAL:
                gold_amount = 1 + int(f.normal_loot_cost_at_lvl(self.level) * multiplier)
            elif self.rarity == RARITY_TYPE.RARE:
                gold_amount = 1 + int(f.rare_loot_cost_at_lvl(self.level) * multiplier)
            elif self.rarity == RARITY_TYPE.EPIC:
                gold_amount = 1 + int(f.epic_loot_cost_at_lvl(self.level) * multiplier)
            else:
                raise ArtifactsException('unknown artifact rarity type: %s' % self)
        else:
            gold_amount = 1 + int(f.sell_artifact_price(self.level) * multiplier)

        return gold_amount

    def serialize(self):
        return {'id': self.id,
                'power': self.power,
                'quest': self.quest,
                'quest_uuid': self.quest_uuid,
                'bag_uuid': self.bag_uuid,
                'level': self.level}


    @classmethod
    def deserialize(cls, storage, data):
        return cls(record=storage.get_artifact_record(data['id']),
                   power=data['power'],
                   quest=data['quest'],
                   quest_uuid=data['quest_uuid'],
                   bag_uuid=data['bag_uuid'],
                   level=data.get('level', 1))

    def ui_info(self):
        return {'type': self.type,
                'equipped': self.equip_type != EQUIP_TYPE.NONE,
                'name': self.name,
                'power': self.power,
                'quest': self.quest}

    def __eq__(self, other):
        return (self.record.id == other.record.id and
                self.quest == other.quest and
                self.power == other.power and
                self.level == other.level and
                self.quest_uuid == other.quest_uuid and
                self.bag_uuid == other.bag_uuid)
