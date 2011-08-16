# -*- coding: utf-8 -*-
import random

def load_effect_from_dict(data):
    effect = EFFECT_CLASSES[data['type']]()
    effect.load_from_dict(data)
    return effect

class RAW_EFFECT_TYPE:
    MIN_DAMAGE = 'min_damage'
    MAX_DAMAGE = 'max_damage'
    BATTLE_SPEED = 'battle_speed'

class Effect(object):
    TYPE = None
    COST = 0
    
    def __init__(self):
        self.lvl = 1
        self.raw_effects = {}

    def lvl_up(self, delta=1):
        self.lvl += delta

    def update(self):
        pass

    def ui_info(self):
        return { 'type': self.TYPE,
                 'raw_effects': self.raw_effects }

    def save_to_dict(self):
        return { 'type': self.TYPE,
                 'lvl': self.lvl,
                 'raw_effects': self.raw_effects }

    def load_from_dict(self, data):
        self.lvl = data['lvl']
        self.raw_effects = data['raw_effects']


class WeaponBase(Effect):

    BATTLE_SPEED_BASE = None
    DAMAGE_BASE = None
    MIN_MAX_DELTA = None
    DAMAGE_VARIANCE = None
    SPEED_VARIANCE = None
    
    def update(self):
        battle_speed = 1 + self.lvl * self.BATTLE_SPEED_BASE
        damage = 1 + self.lvl * self.DAMAGE_BASE

        min_damage = damage * (1-self.MIN_MAX_DELTA + random.uniform(-self.DAMAGE_VARIANCE, self.DAMAGE_VARIANCE) )
        max_damage = damage * (1+self.MIN_MAX_DELTA + random.uniform(-self.DAMAGE_VARIANCE, self.DAMAGE_VARIANCE) )
        battle_speed = battle_speed * (1 + random.uniform(-self.SPEED_VARIANCE, self.SPEED_VARIANCE))

        min_damage, max_damage = min(min_damage, max_damage), max(min_damage, max_damage)

        self.raw_effects[RAW_EFFECT_TYPE.MIN_DAMAGE] = int(round(min_damage))
        self.raw_effects[RAW_EFFECT_TYPE.MAX_DAMAGE] = int(round(max_damage))
        self.raw_effects[RAW_EFFECT_TYPE.BATTLE_SPEED] = battle_speed


class SwordBase(WeaponBase):
    TYPE = 'SWORD_BASE'
    COST = 2

    BATTLE_SPEED_BASE = 0.1
    DAMAGE_BASE = 2    
    MIN_MAX_DELTA = 0.15 
    DAMAGE_VARIANCE = 0.10
    SPEED_VARIANCE = 0.10

EFFECT_CLASSES = dict( (effect.TYPE, effect) 
                       for effect_name, effect in globals().items() 
                       if isinstance(effect, type) and issubclass(effect, Effect) and effect.TYPE is not None)

