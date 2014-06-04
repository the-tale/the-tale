# coding: utf-8
import functools

from the_tale.game.prototypes import TimePrototype

from the_tale.game.balance import constants as c


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
            raise exception_class(message=u'can not push power to place "%s" - current push turn number (%d) less then latest (%d) ' % (self.name, points[-1][0], turn))

        points.append((turn, value))

        current_turn_number = TimePrototype.get_current_turn_number()

        while points and points[0][0] < current_turn_number - history_length:
            points.pop(0)

    push_power.__name__ = method_name

    return push_power



def _create_add_power_evenly(method_name, history_length):

    def add_power_evenly(self, delta):
        cells_number = len(self.power_points)

        turn_number = TimePrototype.get_current_turn_number()

        self.power_points[:] = [ (turn, value+delta/cells_number / (1 - float(turn_number- turn) / history_length))
                                 for turn, value in self.power_points ]

    add_power_evenly.__name__ = method_name

    return add_power_evenly


def _create_fill_power_evenly(method_name, history_length):

    def fill_power_evenly(self, delta):
        turn_number = TimePrototype.get_current_turn_number()

        TURNS_STEP = int(c.TURNS_IN_HOUR)

        cells_number = history_length / TURNS_STEP

        for i in xrange(cells_number):
            turn = turn_number - (cells_number - i) * TURNS_STEP
            divider = 1 - float(turn_number- turn) / history_length

            if divider > 0.01:
                self.power_points.append((turn,  delta/cells_number / divider))


    fill_power_evenly.__name__ = method_name

    return fill_power_evenly



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

        cls.add_power_evenly = _create_add_power_evenly('add_power_evenly', history_length)
        cls.fill_power_evenly = _create_fill_power_evenly('fill_power_evenly', history_length)

        return cls

    return decorator
