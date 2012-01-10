# coding: utf-8
from django_next.utils import s11n

class Context(object):

    def __init__(self):
        self.ability_magick_mushroom = 1


    def after_mob_strike(self):
        self.ability_magick_mushroom = 1

    def after_battle_end(self):
        self.ability_magick_mushroom = 1


    def update_damage_from_hero(self, percents, value):
        return percents * self.ability_magick_mushroom, value * self.ability_magick_mushroom

    
    def serialize(self):
        return s11n.to_json({ 'ability_magick_mushroom': self.ability_magick_mushroom })

    @classmethod
    def deserialize(cls, data):
        data = s11n.from_json(data)
        context = cls()
        context.ability_magick_mushroom = data.get('ability_magick_mushroom', 1)
        return context
