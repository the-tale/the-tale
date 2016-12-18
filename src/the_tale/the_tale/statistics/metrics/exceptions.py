# coding: utf-8

from the_tale.statistics import exceptions


class MetricsError(exceptions.StatisticsError):
    MSG = 'metrics error'


class UnequalDatesError(MetricsError):
    MSG = 'unequal dates'

class ValuesCompletedError(MetricsError):
    MSG = 'values already completed, metric must be reinitialized'
