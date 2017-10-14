
import collections


_TimeBase = collections.namedtuple('_TimeBase', ('hour', 'minute', 'second'))


class Time(_TimeBase):
    __slots__ = ()

    def __new__(cls, hour=0, minute=0, second=0):

        if not isinstance(hour, int):
            raise ValueError('hour must be integer')

        if not 0 <= hour <= 23:
            raise ValueError('hour must be between 0 and 23 inclusive')

        if not isinstance(minute, int):
            raise ValueError('minute must be integer')

        if not 0 <= minute <= 59:
            raise ValueError('minute must be between 0 and 59 inclusive')

        if not isinstance(second, int):
            raise ValueError('second must be integer')

        if not 0 <= second <= 59:
            raise ValueError('second must be between 0 and 59 inclusive')

        return super().__new__(cls, hour=hour, minute=minute, second=second)

    def total_seconds(self):
        return self.hour * 60 * 60 + self.minute * 60 + self.second

    def verbose(self, format='{hour:0>2}:{minute:0>2}'):
        return format.format(hour=self.hour,
                             minute=self.minute,
                             second=self.second)

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.hour == other.hour and
                self.minute == other.minute and
                self.second == other.second)

    def __ne__(self, other):
        return not self.__eq__(other)
