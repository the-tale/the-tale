# -*- coding: utf-8 -*-

class ArtifactPrototype(object):

    def __init__(self, tp=None, quest=False):
        self.type = tp
        self.name = None
        self.effects = []
        self.cost = 0
        self.quest = quest

    def set_name(self, name):
        self.name = name

    def set_cost(self, cost):
        self.cost = cost

    def add_effects(self, effects_list):
        self.effects.extend(effects_list)

    def load_from_dict(self, data):
        self.type = data['type']
        self.name = data['name']
        self.cost = data['cost']
        self.quest = data['quest']
        for effect in data['effects']:
            self.effects.append(effect) #TODO: replace when effects will appear

    def save_to_dict(self):
        return {'type': self.type,
                'name': self.name,
                'cost': self.cost,
                'quest': self.quest,
                'effects': [ effect.save_to_dict() for effect in self.effects]}

    def ui_info(self):
        return {'type': self.type,
                'name': self.name,
                'cost': self.cost,
                'quest': self.quest,
                'effects': [ effect.ui_info() for effect in self.effects]}
