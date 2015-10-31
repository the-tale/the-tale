# coding: utf-8

from the_tale.game.habits import HabitBase
from the_tale.game.relations import HABIT_TYPE


class Habit(HabitBase):
    __slots__ = ()

    @property
    def verbose_value(self):
        return self.interval.place_text


class Honor(Habit):
    __slots__ = ()
    TYPE = HABIT_TYPE.HONOR


class Peacefulness(Habit):
    __slots__ = ()
    TYPE = HABIT_TYPE.PEACEFULNESS
