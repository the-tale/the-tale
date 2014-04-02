# coding: utf-8

import datetime

from the_tale.common.utils.logic import days_range

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.conf import accounts_settings

from the_tale.statistics.metrics.base import BaseMetric
from the_tale.statistics import relations


class AliveAfterBase(BaseMetric):
    TYPE = None
    DAYS = None
    PERIOD = 7 # days

    @classmethod
    def count(cls, date):
        query = AccountPrototype._db_filter(is_fast=False, is_bot=False)
        query = query.filter(created_at__gte=date-datetime.timedelta(days=cls.PERIOD), created_at__lt=date)
        return len([True
                    for active_end_at, created_at in query.values_list('active_end_at', 'created_at')
                    if (active_end_at - created_at - datetime.timedelta(seconds=accounts_settings.ACTIVE_STATE_TIMEOUT)).days > cls.DAYS])

    @classmethod
    def complete_values(cls):
        last_date = cls.last_date()

        for date in days_range(last_date+datetime.timedelta(days=1), datetime.datetime.now()-datetime.timedelta(days=cls.DAYS)):
            cls.store_value(date, cls.count(date))



class AliveAfterDay(AliveAfterBase):
    TYPE = relations.RECORD_TYPE.ALIVE_AFTER_DAY
    DAYS = 1

class AliveAfterWeek(AliveAfterBase):
    TYPE = relations.RECORD_TYPE.ALIVE_AFTER_WEEK
    DAYS = 7

class AliveAfterMonth(AliveAfterBase):
    TYPE = relations.RECORD_TYPE.ALIVE_AFTER_MONTH
    DAYS = 30

class AliveAfter3Month(AliveAfterBase):
    TYPE = relations.RECORD_TYPE.ALIVE_AFTER_3_MONTH
    DAYS = 90

class AliveAfter6Month(AliveAfterBase):
    TYPE = relations.RECORD_TYPE.ALIVE_AFTER_6_MONTH
    DAYS = 180

class AliveAfterYear(AliveAfterBase):
    TYPE = relations.RECORD_TYPE.ALIVE_AFTER_YEAR
    DAYS = 360

class AliveAfter0(AliveAfterBase):
    TYPE = relations.RECORD_TYPE.ALIVE_AFTER_0
    DAYS = 0



class Lifetime(BaseMetric):
    TYPE = relations.RECORD_TYPE.LIFETIME
    PERIOD = 7 # days

    @classmethod
    def lifetime(cls, date):
        query = AccountPrototype._db_filter(is_fast=False, is_bot=False)
        query = query.filter(created_at__gte=date-datetime.timedelta(days=cls.PERIOD), created_at__lt=date)
        lifetimes = [active_end_at - created_at - datetime.timedelta(seconds=accounts_settings.ACTIVE_STATE_TIMEOUT)
                     for active_end_at, created_at in query.values_list('active_end_at', 'created_at') ]

        if not lifetimes:
            return 0

        total_time = reduce(lambda s, v: s+v, lifetimes, datetime.timedelta(seconds=0))
        return float(total_time.days) / len(lifetimes)

    @classmethod
    def complete_values(cls):
        last_date = cls.last_date()

        for date in days_range(last_date+datetime.timedelta(days=1), datetime.datetime.now()):
            cls.store_value(date, cls.lifetime(date))


class LifetimePercent(BaseMetric):
    TYPE = relations.RECORD_TYPE.LIFETIME_PERCENT
    PERIOD = 7 # days

    @classmethod
    def lifetime(cls, date):
        query = AccountPrototype._db_filter(is_fast=False, is_bot=False)
        query = query.filter(created_at__gte=date-datetime.timedelta(days=cls.PERIOD), created_at__lt=date)
        lifetimes = [active_end_at - created_at - datetime.timedelta(seconds=accounts_settings.ACTIVE_STATE_TIMEOUT)
                     for active_end_at, created_at in query.values_list('active_end_at', 'created_at') ]

        if not lifetimes:
            return 0

        total_time = reduce(lambda s, v: s+v, lifetimes, datetime.timedelta(seconds=0))
        lifetime = float(total_time.total_seconds()) / len(lifetimes)
        maximum = (datetime.datetime.now().date() - date).total_seconds()
        return  lifetime / maximum * 100

    @classmethod
    def complete_values(cls):
        last_date = cls.last_date()

        for date in days_range(last_date+datetime.timedelta(days=1), datetime.datetime.now()):
            cls.store_value(date, cls.lifetime(date))
