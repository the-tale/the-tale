# coding: utf-8

from the_tale.statistics import exceptions


class MetricsError(exceptions.StatisticsError):
    MSG = u'metrics error'


class UnequalDatesError(MetricsError):
    MSG = u'unequal dates'

class ValuesCompletedError(MetricsError):
    MSG = u'values already completed, metric must be reinitialized'
