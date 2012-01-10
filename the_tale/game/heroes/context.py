# coding: utf-8
import random

from django_next.utils import s11n

class Context(object):

    def __init__(self):
        self.ability_magick_mushroom = 1
        self.ability_once_mob_miss = 0
        self.ability_once_damage_factor = 1
        self.ability_once_leave_battle = 0


    def after_hero_strike(self):
        self.ability_once_damage_factor = 1
        self.ability_once_leave_battle = 0


    def after_mob_strike(self):
        self.ability_magick_mushroom = 1
        self.ability_once_mob_miss = 0
        self.ability_once_leave_battle = 0


    def after_battle_end(self):
        self.ability_magick_mushroom = 1
        self.ability_once_mob_miss = 0
        self.ability_once_damage_factor = 1
        self.ability_once_leave_battle = 0


    def update_damage_from_hero(self, percents, value):
        return (percents * self.ability_magick_mushroom * self.ability_once_damage_factor, 
                value * self.ability_magick_mushroom * self.ability_once_damage_factor)

    def skip_mob_strike(self):
        if random.uniform(0, 1) < self.ability_once_mob_miss:
            return True
        return False

    def leave_battle(self):
        if random.uniform(0, 1) < self.ability_once_leave_battle:
            return True
        return False

    
    def serialize(self):
        return s11n.to_json({ 'ability_magick_mushroom': self.ability_magick_mushroom,
                              'ability_once_mob_miss': self.ability_once_mob_miss,
                              'ability_once_damage_factor': self.ability_once_damage_factor,
                              'ability_once_leave_battle': self.ability_once_leave_battle})

    @classmethod
    def deserialize(cls, data):
        data = s11n.from_json(data)
        context = cls()

        context.ability_magick_mushroom = data.get('ability_magick_mushroom', 1)
        context.ability_once_mob_miss = data.get('ability_once_mob_miss', 0)
        context.ability_once_damage_factor = data.get('ability_once_damage_factor', 1)
        context.ability_once_leave_battle = data.get('ability_once_leave_battle', 0)

        return context
