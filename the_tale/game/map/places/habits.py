# coding: utf-8

from the_tale.game.habits import HabitBase
from the_tale.game.relations import HABIT_TYPE


class Habit(HabitBase):

    @property
    def verbose_value(self):
        return self.interval.place_text

class Honor(Habit):
    TYPE = HABIT_TYPE.HONOR


class Peacefulness(Habit):
    TYPE = HABIT_TYPE.PEACEFULNESS
