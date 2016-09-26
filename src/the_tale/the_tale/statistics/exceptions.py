# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError


class StatisticsError(TheTaleError):
    MSG = 'statistics error'


class ValueNotSpecifiedError(StatisticsError):
    MSG = 'value not specified for record'

class ValueNotSpecifiedForTypeError(StatisticsError):
    MSG = 'value not specified for record with type %(type)s'


class InvertedDateIntervalError(StatisticsError):
    MSG = 'inverted date intercal (date_to: %(date_to)s, date_from: %(date_from)s)'
