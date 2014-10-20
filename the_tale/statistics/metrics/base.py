# coding: utf-8
import datetime

from django.db import models

from the_tale.common.utils.logic import days_range

from the_tale.statistics.prototypes import RecordPrototype
from the_tale.statistics.conf import statistics_settings
from the_tale.statistics.metrics import exceptions


class BaseMetric(object):
    TYPE = None
    FULL_CLEAR_RECUIRED = False

    def __init__(self):
        self.values_completed = False
        self.last_datetime = None
        self.last_date = None
        self.free_date = None
        self.now_date = None

    def initialize(self):
        self.values_completed = False
        self.last_datetime = self._last_datetime()
        self.last_date = self.last_datetime.date()
        self.free_date = self.last_date + datetime.timedelta(days=1)
        self.now_date = datetime.datetime.now().date() - datetime.timedelta(days=1)


    @classmethod
    def clear(cls):
        RecordPrototype.remove_by_type(cls.TYPE)

    @classmethod
    def _last_datetime(cls):
        try:
            return RecordPrototype._db_filter(type=cls.TYPE).order_by('-date')[0].date
        except IndexError:
            return statistics_settings.START_DATE - datetime.timedelta(days=1)

    def store_value(self, date, value):
        return RecordPrototype.create(type=self.TYPE,
                                      date=date,
                                      value_int=value if self.TYPE.value_type.is_INT else None,
                                      value_float=value if self.TYPE.value_type.is_FLOAT else None)

    def get_value(self, date):
        raise NotImplementedError()

    def _get_interval(self):
        return (self.free_date, datetime.datetime.now().date())

    def complete_values(self):
        if self.values_completed:
            raise exceptions.ValuesCompletedError()

        for date in days_range(*self._get_interval()):
            self.store_value(date, self.get_value(date))
        self.values_completed = True

    def db_date_gt(self, field, date=None):
        if date is None:
            date = self.free_date
        field_attribute = '%s__gt' % field
        return models.Q(**{field_attribute: (date + datetime.timedelta(days=1))})

    def db_date_gte(self, field, date=None):
        if date is None:
            date = self.free_date
        field_attribute = '%s__gt' % field
        return models.Q(**{field_attribute: date})

    def db_date_lt(self, field, date=None):
        if date is None:
            date = self.free_date
        field_attribute = '%s__lt' % field
        return models.Q(**{field_attribute: date})

    def db_date_lte(self, field, date=None):
        if date is None:
            date = self.free_date
        field_attribute = '%s__lt' % field
        return models.Q(**{field_attribute: (date + datetime.timedelta(days=1))})

    def db_date_interval(self, field, days, date=None):
        if date is None:
            date = self.free_date
        field_lt_attribute = '%s__lt' % field
        field_gt_attribute = '%s__gt' % field

        if days > 0:
            return (models.Q(**{field_gt_attribute: date}) &
                    models.Q(**{field_lt_attribute: (date + datetime.timedelta(days=days))}) )
        elif days < 0:
            return (models.Q(**{field_lt_attribute: date + datetime.timedelta(days=1)}) &
                    models.Q(**{field_gt_attribute: (date + datetime.timedelta(days=1+days))}) )
        else:
            return (models.Q(**{field_gt_attribute: date}) &
                    models.Q(**{field_lt_attribute: (date + datetime.timedelta(days=1))}) )

    def db_date_day(self, field, date=None):
        if date is None:
            date = self.free_date
        return self.db_date_interval(field, date=date, days=0)



class BaseCombination(BaseMetric):
    TYPE = None
    SOURCES = []

    @classmethod
    def get_combined_value(cls, *args):
        raise NotImplementedError()

    def complete_values(self):
        sources = []

        for source in self.SOURCES:
            data = RecordPrototype._db_filter(type=source,
                                              date__gt=self.last_date).order_by('date').values_list('date', 'value_int')
            sources.append(data)


        for source_record in zip(*sources):

            dates, values = zip(*source_record)

            if list(dates) != [dates[0]]*len(dates):
                raise exceptions.UnequalDatesError()

            self.store_value(dates[0], self.get_combined_value(*values))


class BasePercentsCombination(BaseCombination):

    def get_combined_value(self, part, total):
        if total:
            return float(part * 100) / total
        else:
            return 0.0

class BasePercentsFromSumCombination(BaseCombination):

    def get_combined_value(self, part, *total):
        divider = sum(total)
        if divider:
            return float(part * 100) / divider
        else:
            return 0.0


class BaseFractionCombination(BaseCombination):

    def get_combined_value(self, part, total):
        if total:
            return float(part) / total
        else:
            return 0.0
