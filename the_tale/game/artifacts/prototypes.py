# -*- coding: utf-8 -*-

from .models import EQUIP_TYPE

from game.journal.template import NounFormatter

class ArtifactPrototype(object):

    def __init__(self, tp=None, equip_type=None, power=0, quest=False, data=None):
        self.type = tp
        self.equip_type = equip_type
        self.name = None
        self.cost = 0
        self.quest = quest
        self.power = power

        self.quest_uuid = None
        self.bag_uuid = None

        self.basic_points_spent = 0

        if data:
            self.deserialize(data)

    @property
    def total_points_spent(self):
        return self.basic_points_spent # + self.effect_points_spent

    def set_name(self, name):
        self.name = name

    def set_name_forms(self, name_forms):
        self.name_forms = name_forms

    def set_cost(self, cost):
        self.cost = cost
        
    def set_bag_uuid(self, uuid):
        self.bag_uuid = uuid

    def set_quest_uuid(self, uuid):
        self.quest_uuid = uuid

    def set_power(self, power):
        self.power = power

    def set_points_spent(self, points):
        self.basic_points_spent = points

    def get_formatter(self):
        return NounFormatter(data=self.name_forms)

    def deserialize(self, data):
        self.type = data.get('type', None)
        self.equip_type = data.get('equip_type', None)
        self.name = data.get('name', '')
        self.name_forms = data.get('name_forms', [self.name, self.name, self.name, self.name, self.name, self.name, ])
        self.cost = data.get('cost', 0)
        self.quest = data.get('quest', False)
        self.power = data.get('power', 1)

        self.quest_uuid = data.get('quest_uuid', False)
        self.bag_uuid = data.get('bag_uuid', False)

        self.basic_points_spent = data.get('basic_points_spent', 0)


    def serialize(self):
        return {'type': self.type,
                'equip_type': self.equip_type,
                'name': self.name,
                'name_forms': self.name_forms,
                'cost': self.cost,
                'power': self.power,
                'quest': self.quest,
                'quest_uuid': self.quest_uuid,
                'bag_uuid': self.bag_uuid,
                'basic_points_spent': self.basic_points_spent}

    def ui_info(self):
        return {'type': self.type,
                'equipped': self.equip_type != EQUIP_TYPE.NONE,
                'name': self.name,
                'power': self.power,
                'quest': self.quest}
