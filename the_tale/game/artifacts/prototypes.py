# -*- coding: utf-8 -*-

from game.artifacts.conf import EQUIP_TYPE

from game.balance import formulas as f

class ArtifactPrototype(object):

    def __init__(self, record=None, power=None, quest=False, quest_uuid=None, bag_uuid=None):
        self.record = record
        self.quest = quest
        self.power = power

        self.quest_uuid = quest_uuid
        self.bag_uuid = bag_uuid


    @property
    def id(self): return self.record.id

    @property
    def type(self): return self.record.type

    @property
    def equip_type(self): return self.record.slot

    @property
    def name(self): return self.record.name

    @property
    def normalized_name(self): return self.record.normalized_name

    @property
    def min_lvl(self): return self.record.min_lvl

    @property
    def max_lvl(self): return self.record.max_lvl

    @property
    def can_be_equipped(self):
        from game.heroes.bag import ARTIFACT_TYPES_TO_SLOTS
        return self.equip_type in ARTIFACT_TYPES_TO_SLOTS

    def set_quest_uuid(self, uuid): self.quest_uuid = uuid

    def set_bag_uuid(self, uuid): self.bag_uuid = uuid

    def serialize(self):
        return {'id': self.id,
                'power': self.power,
                'quest': self.quest,
                'quest_uuid': self.quest_uuid,
                'bag_uuid': self.bag_uuid}


    @classmethod
    def deserialize(cls, storage, data):
        return cls(record=storage.data[data['id']],
                   power=data['power'],
                   quest=data['quest'],
                   quest_uuid=data['quest_uuid'],
                   bag_uuid=data['bag_uuid'])

    def ui_info(self):
        return {'type': self.type,
                'equipped': self.equip_type != EQUIP_TYPE.NONE,
                'name': self.name,
                'power': self.power,
                'quest': self.quest}
