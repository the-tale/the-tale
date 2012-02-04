# -*- coding: utf-8 -*-
import math
import random

def deserialize_effect(data):
    effect = EFFECT_CLASSES[data['type']]()
    effect.deserialize(data)
    return effect

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
        return { 'type': self.TYPE}

    def serialize(self):
        return { 'type': self.TYPE,
                 'lvl': self.lvl}

    def deserialize(self, data):
        self.lvl = data['lvl']

    def get_attr_damage(self):
        return (0, 0)

    def get_attr_armor(self):
        return 0

    def get_attr_battle_speed_multiply(self):
        return 1


class WeaponBase(Effect):
    TYPE = 'WEAPON_BASE'

    DAMAGE_BASE = None
    MIN_MAX_DELTA = None
    DAMAGE_VARIANCE = None
    SPEED_PENALTY = None

    def __init__(self, *argv, **kwargs):
        super(WeaponBase, self).__init__(*argv, **kwargs)
        self.min_damage = 0
        self.max_damage = 0
        self.battle_speed = 0
    
    def update(self):
        damage = 1 + self.lvl * self.DAMAGE_BASE

        min_damage = damage * (1-self.MIN_MAX_DELTA + random.uniform(-self.DAMAGE_VARIANCE, self.DAMAGE_VARIANCE) )
        max_damage = damage * (1+self.MIN_MAX_DELTA + random.uniform(-self.DAMAGE_VARIANCE, self.DAMAGE_VARIANCE) )
        battle_speed = 1 - self.SPEED_PENALTY

        min_damage, max_damage = min(min_damage, max_damage), max(min_damage, max_damage)

        self.min_damage = min_damage
        self.max_damage = max_damage
        self.battle_speed = battle_speed

    def get_attr_damage(self):
        return (self.min_damage, self.max_damage)

    def get_attr_battle_speed_multiply(self):
        return self.battle_speed

    def ui_info(self):
        info = super(WeaponBase, self).ui_info()
        info.update({'min_damage': math.floor(self.min_damage),
                     'max_damage': math.ceil(self.max_damage),
                     'battle_speed': self.battle_speed})
        return info

    def serialize(self):
        data = super(WeaponBase, self).serialize()
        data.update({'min_damage': self.min_damage,
                     'max_damage': self.max_damage,
                     'battle_speed': self.battle_speed})
        return data

    def deserialize(self, data):
        super(WeaponBase, self).deserialize(data)
        self.min_damage = data['min_damage']
        self.max_damage = data['max_damage']
        self.battle_speed = data['battle_speed']


class ArmorBase(Effect):
    TYPE = 'ARMOR_BASE'

    ARMOR_BASE = None
    MIN_MAX_DELTA = None
    SPEED_PENALTY = None

    def __init__(self, *argv, **kwargs):
        super(ArmorBase, self).__init__(*argv, **kwargs)
        self.armor = 0
        self.battle_speed = 0
    
    def update(self):
        armor = 0 + self.lvl * self.ARMOR_BASE

        armor = armor * (1 - random.uniform(-self.MIN_MAX_DELTA, self.MIN_MAX_DELTA) )
        battle_speed = 1 - self.SPEED_PENALTY

        self.armor = armor
        self.battle_speed = battle_speed

    def get_attr_armor(self):
        return self.armor

    def get_attr_battle_speed_multiply(self):
        return self.battle_speed

    def ui_info(self):
        info = super(ArmorBase, self).ui_info()
        info.update({'armor': self.armor,
                     'battle_speed': self.battle_speed})
        return info

    def serialize(self):
        data = super(ArmorBase, self).serialize()
        data.update({'armor': self.armor,
                     'battle_speed': self.battle_speed})
        return data

    def deserialize(self, data):
        super(ArmorBase, self).deserialize(data)
        self.armor = data['armor']
        self.battle_speed = data['battle_speed']


class SwordBase(WeaponBase):
    COST = 2

    DAMAGE_BASE = 2    
    MIN_MAX_DELTA = 0.15 
    DAMAGE_VARIANCE = 0.10
    SPEED_PENALTY = 0.05


class PlateBase(ArmorBase):
    COST = 3

    ARMOR_BASE = 1
    MIN_MAX_DELTA = 0.3
    SPEED_PENALTY = 0.20


EFFECT_CLASSES = dict( (effect.TYPE, effect) 
                       for effect_name, effect in globals().items() 
                       if isinstance(effect, type) and issubclass(effect, Effect) and effect.TYPE is not None)

