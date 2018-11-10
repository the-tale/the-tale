
import smart_imports

smart_imports.all()


class Habit(game_habits.HabitBase):
    __slots__ = ()

    @property
    def verbose_value(self):
        return self.interval.place_text


class Honor(Habit):
    __slots__ = ()
    TYPE = game_relations.HABIT_TYPE.HONOR


class Peacefulness(Habit):
    __slots__ = ()
    TYPE = game_relations.HABIT_TYPE.PEACEFULNESS
