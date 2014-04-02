# coding: utf-8

from the_tale.statistics.prototypes import RecordPrototype
from the_tale.statistics.conf import statistics_settings

class BaseMetric(object):

    TYPE = None

    @classmethod
    def clear(cls):
        RecordPrototype.remove_by_type(cls.TYPE)

    @classmethod
    def last_date(cls):
        try:
            return RecordPrototype._db_filter(type=cls.TYPE).order_by('-date')[0].date
        except IndexError:
            return statistics_settings.START_DATE

    @classmethod
    def complete_values(cls):
        raise NotImplementedError(u'MUST be implemented in child classes')

    @classmethod
    def store_value(cls, date, value):
        return RecordPrototype.create(type=cls.TYPE,
                                      date=date,
                                      value_int=value if cls.TYPE.value_type.is_INT else None,
                                      value_float=value if cls.TYPE.value_type.is_FLOAT else None)
