# coding: utf-8
import functools

from the_tale.game.prototypes import TimePrototype


def _sum_raw_power_points(history_length, points):
    if not points:
        return 0
    turn_number = TimePrototype.get_current_turn_number()
    return sum([power[1]*(1-float(turn_number-power[0])/history_length) for power in points])


def _sum_power_points(history_length, points):
    return max(_sum_raw_power_points(history_length, points), 0)


def _create_power_points_getter(name):
    def power_points(self):
        if name not in self.data:
            self.data[name] = []
        return self.data[name]
    power_points.__name__ = name

    return power_points


def _create_power_points_sum(method_name, history_length, name):

    def power(self):
        return _sum_power_points(history_length, getattr(self, name))

    power.__name__ = method_name

    return power


def _create_raw_power_points_sum(method_name, history_length, name):

    def power(self):
        return _sum_raw_power_points(history_length, getattr(self, name))

    power.__name__ = method_name

    return power

def _create_power_points_push(method_name, history_length, exception_class, name):

    def push_power(self, turn, value):
        points = getattr(self, name)

        if points and points[-1][0] > turn:
            raise exception_class(u'can not push power to place "%s" - current push turn number (%d) less then latest (%d) ' % (self.name, points[-1][0], turn))

        points.append((turn, value))

        current_turn_number = TimePrototype.get_current_turn_number()

        while points and points[0][0] < current_turn_number - history_length:
            points.pop(0)

    push_power.__name__ = method_name

    return push_power



def add_power_management(history_length, exception_class):
    '''
    manage powers in persons and places
    '''

    @functools.wraps(add_power_management)
    def decorator(cls):
        cls.power_points = property(_create_power_points_getter('power_points'))
        cls.power = property(_create_power_points_sum('power', history_length, 'power_points'))
        cls.push_power = _create_power_points_push('push_power', history_length, exception_class, 'power_points')

        cls.raw_power = property(_create_raw_power_points_sum('raw_power', history_length, 'power_points'))

        cls.power_positive_points = property(_create_power_points_getter('power_positive_points'))
        cls.power_positive = property(_create_power_points_sum('power_positive', history_length, 'power_positive_points'))
        cls.push_power_positive = _create_power_points_push('push_power_positive', history_length, exception_class, 'power_positive_points')

        cls.power_negative_points = property(_create_power_points_getter('power_negative_points'))
        cls.power_negative = property(_create_power_points_sum('power_negative', history_length, 'power_negative_points'))
        cls.push_power_negative = _create_power_points_push('push_power_negative', history_length, exception_class, 'power_negative_points')

        return cls

    return decorator
