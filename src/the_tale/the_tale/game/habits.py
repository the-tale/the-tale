
import smart_imports

smart_imports.all()


class HabitBase(object):
    __slots__ = ('owner', 'raw_value', 'intervals', '_interval__lazy')
    TYPE = None

    def __init__(self, raw_value):
        super(HabitBase, self).__init__()
        self.owner = None
        self.raw_value = raw_value

    def set_habit(self, value):
        self.raw_value = max(-c.HABITS_BORDER, min(c.HABITS_BORDER, value))

    @utils_decorators.lazy_property
    def interval(self):
        for interval, right_border in zip(self.TYPE.intervals.records, c.HABITS_RIGHT_BORDERS):
            if right_border > self.raw_value:
                return interval

    @property
    def verbose_value(self):
        raise NotImplementedError()

    def reset_accessors_cache(self):
        pass

    @property
    def increase_modifier(self):
        return 1

    @property
    def decrease_modifier(self):
        return 1

    def change(self, delta):
        if (self.raw_value > 0 and delta > 0) or (self.raw_value < 0 and delta < 0):
            delta *= self.increase_modifier
        elif (self.raw_value < 0 and delta > 0) or (self.raw_value > 0 and delta < 0):
            delta *= self.decrease_modifier

        self.set_habit(self.raw_value + delta)

        del self.interval

        self.reset_accessors_cache()

    def modify_attribute(self, modifier, value):
        return value

    def check_attribute(self, modifier):
        return False

    def update_context(self, actor, enemy):
        pass
