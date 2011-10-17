# -*- coding: utf-8 -*-
from .effects import deserialize_effect

class ArtifactPrototype(object):

    def __init__(self, tp=None, equip_type=None, quest=False, data=None):
        self.type = tp
        self.equip_type = equip_type
        self.name = None
        self.effects = []
        self.cost = 0
        self.quest = quest

        self.quest_uuid = None
        self.bag_uuid = None

        self.basic_points_spent = 0
        self.effect_points_spent = 0

        if data:
            self.deserialize(data)

    @property
    def total_points_spent(self):
        return self.basic_points_spent + self.effect_points_spent

    def set_name(self, name):
        self.name = name

    def set_cost(self, cost):
        self.cost = cost
        
    def set_bag_uuid(self, uuid):
        self.bag_uuid = uuid

    def set_quest_uuid(self, uuid):
        self.quest_uuid = uuid

    def add_effects(self, effects_list):
        self.effects.extend(effects_list)

    def get_attr_damage(self):
        damage = (0, 0)
        for effect in self.effects: 
            effect_damage = effect.get_attr_damage()
            damage = (damage[0] + effect_damage[0], damage[1] + effect_damage[1])
        return damage

    def get_attr_battle_speed_multiply(self):
        penalty = 1
        for effect in self.effects:
            effect_penalty = effect.get_attr_battle_speed_multiply()
            penalty *= effect_penalty
        return penalty

    def get_attr_armor(self):
        armor = 0
        for effect in self.effects: 
            effect_armor = effect.get_attr_armor()
            armor += effect_armor
        return armor


    def deserialize(self, data):
        self.type = data.get('type', None)
        self.equip_type = data.get('equip_type', None)
        self.name = data.get('name', '')
        self.cost = data.get('cost', 0)
        self.quest = data.get('quest', False)

        self.quest_uuid = data.get('quest_uuid', False)
        self.bag_uuid = data.get('bag_uuid', False)

        self.basic_points_spent = data.get('basic_points_spent', 0)
        self.effect_points_spent = data.get('effect_points_spent', 0)

        for effect in data['effects']:
            self.effects.append(deserialize_effect(effect))

    def serialize(self):
        return {'type': self.type,
                'equip_type': self.equip_type,
                'name': self.name,
                'cost': self.cost,
                'quest': self.quest,
                'quest_uuid': self.quest_uuid,
                'bag_uuid': self.bag_uuid,
                'basic_points_spent': self.basic_points_spent,
                'effect_points_spent': self.effect_points_spent,
                'effects': [ effect.serialize() for effect in self.effects]}

    def ui_info(self):
        return {'type': self.type,
                'equip_type': self.equip_type,
                'name': self.name,
                'cost': self.cost,
                'quest': self.quest,
                'effects': [ effect.ui_info() for effect in self.effects]}
