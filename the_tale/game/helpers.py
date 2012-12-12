# coding: utf-8
import functools

def add_power_management(history_length, exception_class):
    '''
    manage powers in persons and places
    '''

    @functools.wraps(add_power_management)
    def decorator(cls):

        def power_points(self):
            if 'power_points' not in self.data:
                self.data['power_points'] = []
            return self.data['power_points']

        def power(self):
            if self.power_points:
                return max(sum([power[1] for power in self.power_points]), 0)
            return 0

        def push_power(self, turn, value):
            if self.power_points and self.power_points[-1][0] > turn:
                raise exception_class(u'can not push power to place "%s" - current push turn number (%d) less then latest (%d) ' % (self.name, self.power_points[-1][0], turn))

            self.power_points.append((turn, value))

            while self.power_points and self.power_points[0][0] < turn - history_length:
                self.power_points.pop(0)


        cls.power_points = property(power_points)
        cls.power = property(power)
        cls.push_power = push_power

        return cls

    return decorator
