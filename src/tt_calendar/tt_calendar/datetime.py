

from . import date
from . import time


class DateTime(object):
    __slots__ = ('date', 'time')

    def __init__(self, year=0, month=0, day=0, hour=0, minute=0, second=0):
        self.date = date.Date(year=year, month=month, day=day)
        self.time = time.Time(hour=hour, minute=minute, second=second)

    def replace(self, year=None, month=None, day=None, hour=None, minute=None, second=None):
        return self.__class__(year=year if year is not None else self.year,
                              month=month if month is not None else self.month,
                              day=day if day is not None else self.day,
                              hour=hour if hour is not None else self.hour,
                              minute=minute if minute is not None else self.minute,
                              second=second if second is not None else self.second)

    @property
    def year(self): return self.date.year

    @property
    def month(self): return self.date.month

    @property
    def quint(self): return self.date.quint

    @property
    def quint_day(self): return self.date.quint_day

    @property
    def day(self): return self.date.day

    @property
    def hour(self): return self.time.hour

    @property
    def minute(self): return self.time.minute

    @property
    def second(self): return self.time.second

    def verbose_full(self):
        return '{} {}'.format(self.date.verbose_full(), self.time.verbose())

    def verbose_short(self):
        return '{} {}'.format(self.date.verbose_short(), self.time.verbose())

    def total_seconds(self):
        return self.date.total_seconds() + self.time.total_seconds()

    @classmethod
    def from_seconds(cls, seconds):
        from . import converters
        return converters.converter.from_seconds(seconds)

    def __add__(self, other):
        return self.from_seconds(self.total_seconds() + other.total_seconds())

    def __sub__(self, other):
        return self.from_seconds(self.total_seconds() - other.total_seconds())

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.date == other.date and
                self.time == other.time)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return 'DateTime(year={}, month={}, day={}, hour={}, minute={}, second={})'.format(self.year,
                                                                                           self.month,
                                                                                           self.day,
                                                                                           self.hour,
                                                                                           self.minute,
                                                                                           self.second)
