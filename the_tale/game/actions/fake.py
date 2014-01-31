# coding: utf-8

from the_tale.game.actions.contexts.battle import BattleContext

class FakeActor(object):

    def __init__(self, name='fake_actor', damage=10, max_health=100, context=None, level=7, mob_type=None):
        self.name = name
        self.basic_damage = damage
        self.max_health = max_health
        self.health = max_health
        self.level = level
        self.context = context if context else BattleContext()
        self.mob_type = mob_type

    @property
    def initiative(self): return 1

    @property
    def normalized_name(self): return 'normalized_%s' % self.name

    def change_health(self, value):
        old_health = self.health
        self.health = int(max(0, min(self.health + value, self.max_health)))
        return int(self.health - old_health)

    def choose_ability(self):
        raise NotImplementedError
