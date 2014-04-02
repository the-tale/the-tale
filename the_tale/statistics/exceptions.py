# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError


class StatisticsError(TheTaleError):
    MSG = u'statistics error'


class ValueNotSpecifiedError(StatisticsError):
    MSG = u'value not specified for record'

class ValueNotSpecifiedForTypeError(StatisticsError):
    MSG = u'value not specified for record with type %(type)s'


class InvertedDateIntervalError(StatisticsError):
    MSG = u'inverted date intercal (date_to: %(date_to)s, date_from: %(date_from)s)'
