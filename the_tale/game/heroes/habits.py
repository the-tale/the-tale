# coding: utf-8

import random

from the_tale.common.utils.decorators import lazy_property

from the_tale.game.mobs.storage import mobs_storage

from the_tale.game.balance import constants as c



class Habit(object):
    __slots__ = ('hero', 'field_name', 'intervals', '_interval__lazy')

    def __init__(self, hero, name, intervals):
        super(Habit, self).__init__()
        self.hero = hero
        self.field_name = 'habit_%s' % name
        self.intervals = intervals

    @property
    def raw_value(self):
        return getattr(self.hero._model, self.field_name)

    @lazy_property
    def interval(self):
        for interval, right_border in zip(self.intervals.records, c.HABITS_RIGHT_BORDERS):
            if right_border > self.raw_value:
                return interval

    @property
    def verbose_value(self):
        if self.hero.gender.is_MASCULINE:
            return self.interval.text
        if self.hero.gender.is_FEMININE:
            return self.interval.female_text
        return self.interval.neuter_text

    def change(self, delta):
        setattr(self.hero._model, self.field_name, max(-c.HABITS_BORDER, min(c.HABITS_BORDER, self.raw_value + delta)))
        del self.interval


    def modify_attribute(self, modifier, value):
        return value

    def check_attribute(self, modifier):
        return False

    def update_context(self, actor, enemy):
        pass



class Honor(Habit):

    def modify_attribute(self, modifier, value):
        if self.interval.is_LEFT_3 and modifier.is_POWER_TO_ENEMY:
            return value * (1 + c.HONOR_POWER_BONUS_FRACTION)

        if self.interval.is_RIGHT_3 and modifier.is_POWER_TO_FRIEND:
            return value * (1 + c.HONOR_POWER_BONUS_FRACTION)

        return value

    def check_attribute(self, modifier):
        if self.interval.is_LEFT_3 and modifier.is_KILL_BEFORE_BATTLE:
            return random.uniform(0, 1) < c.KILL_BEFORE_BATTLE_PROBABILITY

        if self.interval.is_RIGHT_3 and modifier.is_PICKED_UP_IN_ROAD:
            return random.uniform(0, 1) < c.PICKED_UP_IN_ROAD_PROBABILITY

        return False

    def update_context(self, actor, enemy):
        if (self.interval.is_LEFT_2 or self.interval.is_LEFT_3) and enemy.mob_type is not None and enemy.mob_type.is_CIVILIZED:
            actor.context.use_crit_chance(c.MONSTER_TYPE_BATTLE_CRIT_MAX_CHANCE * mobs_storage.mob_type_fraction(enemy.mob_type))

        if (self.interval.is_RIGHT_2 or self.interval.is_RIGHT_3) and enemy.mob_type is not None and enemy.mob_type.is_MONSTER:
            actor.context.use_crit_chance(c.MONSTER_TYPE_BATTLE_CRIT_MAX_CHANCE * mobs_storage.mob_type_fraction(enemy.mob_type))


class Aggressiveness(Habit):

    def modify_attribute(self, modifier, value):
        return value

    def check_attribute(self, modifier):
        return False

    def update_context(self, actor, enemy):
        pass
