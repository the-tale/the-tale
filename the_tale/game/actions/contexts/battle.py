# coding: utf-8
import random

class BattleContext(object):

    def __init__(self):
        self.ability_magic_mushroom = []
        self.ability_sidestep = []
        self.stun_length = 0

    def use_ability_magic_mushroom(self, damage_factors): self.ability_magic_mushroom = [None] + damage_factors

    def use_ability_sidestep(self, miss_probabilities): self.ability_sidestep = [None] + miss_probabilities

    def use_stun(self, stun_length): self.stun_length = max(self.stun_length, stun_length + 1)

    @property
    def is_stunned(self): return (self.stun_length > 0)

    def should_miss_attack(self):
        if not self.ability_sidestep:
            return False
        return (random.uniform(0, 1) < self.ability_sidestep[0])

    def modify_initial_damage(self, damage):
        if self.ability_magic_mushroom:
            damage = damage * self.ability_magic_mushroom[0]
        return int(round(damage))

    def on_own_turn(self):
        if self.ability_magic_mushroom:
            self.ability_magic_mushroom.pop(0)
        if self.ability_sidestep:
            self.ability_sidestep.pop(0)
        if self.stun_length:
            self.stun_length -= 1


    def serialize(self):
        return { 'ability_magic_mushroom': self.ability_magic_mushroom,
                 'ability_sidestep': self.ability_sidestep,
                 'stun_length': self.stun_length }

    @classmethod
    def deserialize(cls, data):
        context = cls()

        context.ability_magic_mushroom = data.get('ability_magic_mushroom', [])
        context.ability_sidestep = data.get('ability_sidestep', [])
        context.stun_turns = data.get('stun_length', 0)

        return context
