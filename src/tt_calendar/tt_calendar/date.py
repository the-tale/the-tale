
import collections

from . import relations


_DateBase = collections.namedtuple('_DateBase', ('year', 'month', 'day'))


class Date(_DateBase):
    __slots__ = ()

    def __new__(cls, year=0, month=0, day=0):

        if not isinstance(year, int):
            raise ValueError('year must be integer')

        if year < 0:
            raise ValueError('year must be greater 0 or equal to 0')

        if not isinstance(month, int):
            raise ValueError('month must be integer')

        if not 0 <= month <= 3:
            raise ValueError('month must be between 0 and 3 inclusive')

        if not isinstance(day, int):
            raise ValueError('day must be integer')

        if not 0 <= day <= 89:
            raise ValueError('day must be between 0 and 89 inclusive')

        return super().__new__(cls, year=year, month=month, day=day)

    @property
    def quint(self): return self.day // 15

    @property
    def quint_day(self): return self.day % 15

    @property
    def month_type(self): return relations.MONTH(self.month)

    @property
    def quint_type(self): return relations.QUINT(self.quint)

    @property
    def quint_day_type(self): return relations.QUINT_DAY(self.quint_day)

    def total_seconds(self):
        from . import converters
        return (self.year * converters.converter.seconds_in_year +
                self.month * converters.converter.seconds_in_month +
                self.day * converters.converter.seconds_in_day)

    def verbose_full(self):
        return '{day} {quint} {month} {year} года'.format(day=self.quint_day+1,
                                                          quint=relations.QUINT(self.quint).date_text,
                                                          month=relations.MONTH(self.month).date_text,
                                                          year=self.year+1)

    def verbose_short(self):
        return '{day}.{month}.{year}'.format(day=self.day+1,
                                             month=self.month+1,
                                             year=self.year+1)

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.year == other.year and
                self.month == other.month and
                self.day == other.day)

    def __ne__(self, other):
        return not self.__eq__(other)
