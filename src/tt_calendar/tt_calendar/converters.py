
from . import datetime


class BaseConverter(object):
    __slots__ = ('seconds_in_hour', 'seconds_in_day', 'seconds_in_month', 'seconds_in_year')

    SECONDS_IN_TURN = NotImplemented

    SECONDS_IN_MINUTE = 60
    MINUTES_IN_HOUR = 60
    HOURSE_IN_DAY = 24

    DAYS_IN_MONTH = NotImplemented
    MONTH_IN_YEAR = 4

    def __init__(self):
        self.seconds_in_hour = self.SECONDS_IN_MINUTE * self.MINUTES_IN_HOUR
        self.seconds_in_day = self.seconds_in_hour * self.HOURSE_IN_DAY
        self.seconds_in_month = self.seconds_in_day * self.DAYS_IN_MONTH
        self.seconds_in_year = self.seconds_in_month * self.MONTH_IN_YEAR

    def from_turns(self, turns):
        return self.from_seconds(turns * self.SECONDS_IN_TURN)

    def from_seconds(self, seconds):
        year = seconds // self.seconds_in_year
        seconds %= self.seconds_in_year

        month = seconds // self.seconds_in_month
        seconds %= self.seconds_in_month

        day = seconds // self.seconds_in_day
        seconds %= self.seconds_in_day

        hour = seconds // self.seconds_in_hour
        seconds %= self.seconds_in_hour

        minute = seconds // self.SECONDS_IN_MINUTE
        seconds %= self.SECONDS_IN_MINUTE

        second = seconds

        return datetime.DateTime(year, month, day, hour, minute, second)


class ConverterV1(BaseConverter):
    __slots__ = ()

    SECONDS_IN_TURN = 120
    DAYS_IN_MONTH = 4 * 7

    def from_seconds(self, seconds):
        v1_datetime = super().from_seconds(seconds)

        # поскольку в актуальному календаре в месяце 90 дней вместо 28
        # нормируем количество дней, чтобы даты были разнесены равномерно

        day = int(v1_datetime.day * 90 / self.DAYS_IN_MONTH)

        return v1_datetime.replace(day=day)


class ConverterV2(BaseConverter):
    __slots__ = ('old_converter',)

    SECONDS_IN_TURN = 60
    DAYS_IN_MONTH = 90
    TURNS_BARRIER = 16620000

    def __init__(self):
        super().__init__()
        self.old_converter = ConverterV1()

    def from_turns(self, turns):
        old_turns = min(self.TURNS_BARRIER, turns)
        old_datetime = self.old_converter.from_turns(old_turns)

        new_turns = turns - old_turns

        if new_turns <= 0:
            return old_datetime

        return old_datetime + super().from_turns(new_turns)


converter = ConverterV2()
