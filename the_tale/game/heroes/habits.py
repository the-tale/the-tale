# coding: utf-8

import random

from questgen.relations import OPTION_MARKERS as QUEST_OPTION_MARKERS

from the_tale.game.mobs.storage import mobs_storage

from the_tale.game.balance import constants as c

from the_tale.game.actions.relations import ACTION_EVENT

from the_tale.game.habits import HabitBase
from the_tale.game import relations as game_relations

from the_tale.accounts.achievements.storage import achievements_storage
from the_tale.accounts.achievements.relations import ACHIEVEMENT_TYPE


class Habit(HabitBase):
    __slots__ = ()

    @property
    def _real_interval(self):
        if self.owner.clouded_mind:
            return random.choice(self.TYPE.intervals.records)
        return self.interval

    @property
    def verbose_value(self):
        if self.owner.gender.is_MASCULINE:
            return self.interval.text
        if self.owner.gender.is_FEMININE:
            return self.interval.female_text
        return self.interval.neuter_text

    def reset_accessors_cache(self):
        self.owner.reset_accessors_cache()

    @property
    def increase_modifier(self):
        return self.owner.habits_increase_modifier

    @property
    def decrease_modifier(self):
        return self.owner.habits_decrease_modifier


class Honor(Habit):
    __slots__ = ()

    TYPE = game_relations.HABIT_TYPE.HONOR

    def change(self, delta):
        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.HABITS_HONOR, object=self.owner):
            super(Honor, self).change(delta)

    def modify_attribute(self, modifier, value):
        if modifier.is_POWER_TO_ENEMY and self._real_interval.is_LEFT_3:
            return value + c.HONOR_POWER_BONUS_FRACTION

        if modifier.is_POWER_TO_FRIEND and self._real_interval.is_RIGHT_3:
            return value + c.HONOR_POWER_BONUS_FRACTION

        if modifier.is_QUEST_MARKERS and (self._real_interval.is_LEFT_1 or self._real_interval.is_LEFT_2 or self._real_interval.is_LEFT_3):
            value[QUEST_OPTION_MARKERS.DISHONORABLE] = abs(self.raw_value / float(c.HABITS_BORDER))
            return value

        if modifier.is_QUEST_MARKERS and (self._real_interval.is_RIGHT_1 or self._real_interval.is_RIGHT_2 or self._real_interval.is_RIGHT_3):
            value[QUEST_OPTION_MARKERS.HONORABLE] = abs(self.raw_value / float(c.HABITS_BORDER))
            return value

        if modifier.is_QUEST_MARKERS_REWARD_BONUS and (self._real_interval.is_LEFT_1 or self._real_interval.is_LEFT_2 or self._real_interval.is_LEFT_3):
            value[QUEST_OPTION_MARKERS.DISHONORABLE] = abs(self.raw_value / float(c.HABITS_BORDER)) * c.HABIT_QUEST_REWARD_MAX_BONUS
            return value

        if modifier.is_QUEST_MARKERS_REWARD_BONUS and (self._real_interval.is_RIGHT_1 or self._real_interval.is_RIGHT_2 or self._real_interval.is_RIGHT_3):
            value[QUEST_OPTION_MARKERS.HONORABLE] = abs(self.raw_value / float(c.HABITS_BORDER)) * c.HABIT_QUEST_REWARD_MAX_BONUS
            return value

        if modifier.is_HONOR_EVENTS and (self._real_interval.is_RIGHT_2 or self._real_interval.is_RIGHT_3):
            value.add(ACTION_EVENT.NOBLE)
            return value

        if modifier.is_HONOR_EVENTS and (self._real_interval.is_LEFT_2 or self._real_interval.is_LEFT_3):
            value.add(ACTION_EVENT.DISHONORABLE)
            return value

        return value

    def check_attribute(self, modifier):
        if self._real_interval.is_LEFT_3 and modifier.is_KILL_BEFORE_BATTLE:
            return random.uniform(0, 1) < c.KILL_BEFORE_BATTLE_PROBABILITY

        if self._real_interval.is_RIGHT_3 and modifier.is_PICKED_UP_IN_ROAD:
            return random.uniform(0, 1) < c.PICKED_UP_IN_ROAD_PROBABILITY

        return False

    def update_context(self, actor, enemy):
        if (self._real_interval.is_LEFT_2 or self._real_interval.is_LEFT_3) and enemy.mob_type is not None and enemy.mob_type.is_CIVILIZED:
            actor.context.use_crit_chance(c.MONSTER_TYPE_BATTLE_CRIT_MAX_CHANCE / mobs_storage.mob_type_fraction(enemy.mob_type))

        if (self._real_interval.is_RIGHT_2 or self._real_interval.is_RIGHT_3) and enemy.mob_type is not None and enemy.mob_type.is_MONSTER:
            actor.context.use_crit_chance(c.MONSTER_TYPE_BATTLE_CRIT_MAX_CHANCE / mobs_storage.mob_type_fraction(enemy.mob_type))



class Peacefulness(Habit):
    __slots__ = ()

    TYPE = game_relations.HABIT_TYPE.PEACEFULNESS

    def change(self, delta):
        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.HABITS_PEACEFULNESS, object=self.owner):
            super(Peacefulness, self).change(delta)

    def modify_attribute(self, modifier, value):

        if modifier.is_FRIEND_QUEST_PRIORITY and self._real_interval.is_RIGHT_3:
            return value * c.HABIT_QUEST_PRIORITY_MODIFIER

        if modifier.is_ENEMY_QUEST_PRIORITY and self._real_interval.is_LEFT_3:
            return value * c.HABIT_QUEST_PRIORITY_MODIFIER

        if modifier.is_LOOT_PROBABILITY and (self._real_interval.is_RIGHT_2 or self._real_interval.is_RIGHT_3):
            return value * c.HABIT_LOOT_PROBABILITY_MODIFIER

        if modifier.is_QUEST_MARKERS and (self._real_interval.is_LEFT_1 or self._real_interval.is_LEFT_2 or self._real_interval.is_LEFT_3):
            value[QUEST_OPTION_MARKERS.AGGRESSIVE] =  abs(self.raw_value / float(c.HABITS_BORDER))
            return value

        if modifier.is_QUEST_MARKERS and (self._real_interval.is_RIGHT_1 or self._real_interval.is_RIGHT_2 or self._real_interval.is_RIGHT_3):
            value[QUEST_OPTION_MARKERS.UNAGGRESSIVE] = abs(self.raw_value / float(c.HABITS_BORDER))
            return value

        if modifier.is_QUEST_MARKERS_REWARD_BONUS and (self._real_interval.is_LEFT_1 or self._real_interval.is_LEFT_2 or self._real_interval.is_LEFT_3):
            value[QUEST_OPTION_MARKERS.AGGRESSIVE] = abs(self.raw_value / float(c.HABITS_BORDER)) * c.HABIT_QUEST_REWARD_MAX_BONUS
            return value

        if modifier.is_QUEST_MARKERS_REWARD_BONUS and (self._real_interval.is_RIGHT_1 or self._real_interval.is_RIGHT_2 or self._real_interval.is_RIGHT_3):
            value[QUEST_OPTION_MARKERS.UNAGGRESSIVE] = abs(self.raw_value / float(c.HABITS_BORDER)) * c.HABIT_QUEST_REWARD_MAX_BONUS
            return value

        if modifier.is_HONOR_EVENTS and (self._real_interval.is_RIGHT_2 or self._real_interval.is_RIGHT_3):
            value.add(ACTION_EVENT.PEACEABLE)
            return value

        if modifier.is_HONOR_EVENTS and (self._real_interval.is_LEFT_2 or self._real_interval.is_LEFT_3):
            value.add(ACTION_EVENT.AGGRESSIVE)
            return value


        return value


    def check_attribute(self, modifier):
        if modifier.is_EXP_FOR_KILL and self._real_interval.is_LEFT_3:
            return random.uniform(0, 1) < c.EXP_FOR_KILL_PROBABILITY

        if modifier.is_PEACEFULL_BATTLE and self._real_interval.is_RIGHT_3:
            return random.uniform(0, 1) < c.PEACEFULL_BATTLE_PROBABILITY / mobs_storage.mob_type_fraction(game_relations.BEING_TYPE.CIVILIZED)

        return False

    def update_context(self, actor, enemy):
        if (self._real_interval.is_LEFT_2 or self._real_interval.is_LEFT_3) and enemy.mob_type is not None:
            actor.context.use_first_strike()
