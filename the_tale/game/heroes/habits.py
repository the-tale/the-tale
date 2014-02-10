# coding: utf-8

import random

from questgen.relations import OPTION_MARKERS as QUEST_OPTION_MARKERS

from the_tale.common.utils.decorators import lazy_property

from the_tale.game.mobs.storage import mobs_storage
from the_tale.game.mobs.relations import MOB_TYPE

from the_tale.game.balance import constants as c

from the_tale.game.actions.relations import ACTION_EVENT

from the_tale.game.heroes import relations



class Habit(object):
    __slots__ = ('hero', 'field_name', 'intervals', '_interval__lazy')

    TYPE = None

    def __init__(self, hero, name):
        super(Habit, self).__init__()
        self.hero = hero
        self.field_name = 'habit_%s' % name

    @property
    def raw_value(self):
        return getattr(self.hero._model, self.field_name)

    @lazy_property
    def interval(self):
        for interval, right_border in zip(self.TYPE.intervals.records, c.HABITS_RIGHT_BORDERS):
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

    TYPE = relations.HABIT_TYPE.HONOR

    def modify_attribute(self, modifier, value):
        if modifier.is_POWER_TO_ENEMY and self.interval.is_LEFT_3:
            return value * (1 + c.HONOR_POWER_BONUS_FRACTION)

        if modifier.is_POWER_TO_FRIEND and self.interval.is_RIGHT_3:
            return value * (1 + c.HONOR_POWER_BONUS_FRACTION)

        if modifier.is_QUEST_MARKERS and (self.interval.is_LEFT_1 or self.interval.is_LEFT_2 or self.interval.is_LEFT_3):
            if random.uniform(0, 1) < abs(self.raw_value / float(c.HABITS_BORDER)):
                value.add(QUEST_OPTION_MARKERS.DISHONORABLE)
            return value

        if modifier.is_QUEST_MARKERS and (self.interval.is_RIGHT_1 or self.interval.is_RIGHT_2 or self.interval.is_RIGHT_3):
            if random.uniform(0, 1) < abs(self.raw_value / float(c.HABITS_BORDER)):
                value.add(QUEST_OPTION_MARKERS.HONORABLE)
            return value

        if modifier.is_QUEST_MARKERS_REWARD_BONUS and (self.interval.is_LEFT_1 or self.interval.is_LEFT_2 or self.interval.is_LEFT_3):
            value[QUEST_OPTION_MARKERS.DISHONORABLE] = abs(self.raw_value / float(c.HABITS_BORDER)) * c.HABIT_QUEST_REWARD_MAX_BONUS
            return value

        if modifier.is_QUEST_MARKERS_REWARD_BONUS and (self.interval.is_RIGHT_1 or self.interval.is_RIGHT_2 or self.interval.is_RIGHT_3):
            value[QUEST_OPTION_MARKERS.HONORABLE] = abs(self.raw_value / float(c.HABITS_BORDER)) * c.HABIT_QUEST_REWARD_MAX_BONUS
            return value

        if modifier.is_HONOR_EVENTS and (self.interval.is_RIGHT_2 or self.interval.is_RIGHT_3):
            value.add(ACTION_EVENT.NOBLE)
            return value

        if modifier.is_HONOR_EVENTS and (self.interval.is_LEFT_2 or self.interval.is_LEFT_3):
            value.add(ACTION_EVENT.DISHONORABLE)
            return value

        return value

    def check_attribute(self, modifier):
        if self.interval.is_LEFT_3 and modifier.is_KILL_BEFORE_BATTLE:
            return random.uniform(0, 1) < c.KILL_BEFORE_BATTLE_PROBABILITY

        if self.interval.is_RIGHT_3 and modifier.is_PICKED_UP_IN_ROAD:
            return random.uniform(0, 1) < c.PICKED_UP_IN_ROAD_PROBABILITY

        return False

    def update_context(self, actor, enemy):
        if (self.interval.is_LEFT_2 or self.interval.is_LEFT_3) and enemy.mob_type is not None and enemy.mob_type.is_CIVILIZED:
            actor.context.use_crit_chance(c.MONSTER_TYPE_BATTLE_CRIT_MAX_CHANCE / mobs_storage.mob_type_fraction(enemy.mob_type))

        if (self.interval.is_RIGHT_2 or self.interval.is_RIGHT_3) and enemy.mob_type is not None and enemy.mob_type.is_MONSTER:
            actor.context.use_crit_chance(c.MONSTER_TYPE_BATTLE_CRIT_MAX_CHANCE / mobs_storage.mob_type_fraction(enemy.mob_type))



class Aggressiveness(Habit):

    TYPE = relations.HABIT_TYPE.AGGRESSIVENESS

    def modify_attribute(self, modifier, value):

        if modifier.is_FRIEND_QUEST_PRIORITY and self.interval.is_RIGHT_3:
            return value * c.HABIT_QUEST_PRIORITY_MODIFIER

        if modifier.is_ENEMY_QUEST_PRIORITY and self.interval.is_LEFT_3:
            return value * c.HABIT_QUEST_PRIORITY_MODIFIER

        if modifier.is_LOOT_PROBABILITY and (self.interval.is_RIGHT_2 or self.interval.is_RIGHT_3):
            return value * c.HABIT_LOOT_PROBABILITY_MODIFIER

        if modifier.is_QUEST_MARKERS and (self.interval.is_LEFT_1 or self.interval.is_LEFT_2 or self.interval.is_LEFT_3):
            if random.uniform(0, 1) < abs(self.raw_value / float(c.HABITS_BORDER)):
                value.add(QUEST_OPTION_MARKERS.AGGRESSIVE)
            return value

        if modifier.is_QUEST_MARKERS and (self.interval.is_RIGHT_1 or self.interval.is_RIGHT_2 or self.interval.is_RIGHT_3):
            if random.uniform(0, 1) < abs(self.raw_value / float(c.HABITS_BORDER)):
                value.add(QUEST_OPTION_MARKERS.UNAGGRESSIVE)
            return value

        if modifier.is_QUEST_MARKERS_REWARD_BONUS and (self.interval.is_LEFT_1 or self.interval.is_LEFT_2 or self.interval.is_LEFT_3):
            value[QUEST_OPTION_MARKERS.AGGRESSIVE] = abs(self.raw_value / float(c.HABITS_BORDER)) * c.HABIT_QUEST_REWARD_MAX_BONUS
            return value

        if modifier.is_QUEST_MARKERS_REWARD_BONUS and (self.interval.is_RIGHT_1 or self.interval.is_RIGHT_2 or self.interval.is_RIGHT_3):
            value[QUEST_OPTION_MARKERS.UNAGGRESSIVE] = abs(self.raw_value / float(c.HABITS_BORDER)) * c.HABIT_QUEST_REWARD_MAX_BONUS
            return value

        if modifier.is_HONOR_EVENTS and (self.interval.is_RIGHT_2 or self.interval.is_RIGHT_3):
            value.add(ACTION_EVENT.PEACEABLE)
            return value

        if modifier.is_HONOR_EVENTS and (self.interval.is_LEFT_2 or self.interval.is_LEFT_3):
            value.add(ACTION_EVENT.AGGRESSIVE)
            return value


        return value


    def check_attribute(self, modifier):
        if modifier.is_FIRST_STRIKE and (self.interval.is_LEFT_3 or self.interval.is_LEFT_2):
            return True

        if modifier.is_EXP_FOR_KILL and self.interval.is_LEFT_3:
            return random.uniform(0, 1) < c.EXP_FOR_KILL_PROBABILITY

        if modifier.is_PEACEFULL_BATTLE and self.interval.is_RIGHT_3:
            return random.uniform(0, 1) < c.PEACEFULL_BATTLE_PROBABILITY / mobs_storage.mob_type_fraction(MOB_TYPE.CIVILIZED)

        return False

    def update_context(self, actor, enemy):
        pass
