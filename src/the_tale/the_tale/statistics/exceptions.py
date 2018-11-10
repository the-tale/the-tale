
import smart_imports

smart_imports.all()


class StatisticsError(utils_exceptions.TheTaleError):
    MSG = 'statistics error'


class ValueNotSpecifiedError(StatisticsError):
    MSG = 'value not specified for record'


class ValueNotSpecifiedForTypeError(StatisticsError):
    MSG = 'value not specified for record with type %(type)s'


class InvertedDateIntervalError(StatisticsError):
    MSG = 'inverted date intercal (date_to: %(date_to)s, date_from: %(date_from)s)'


class MetricsError(StatisticsError):
    MSG = 'metrics error'


class UnequalDatesError(MetricsError):
    MSG = 'unequal dates'


class ValuesCompletedError(MetricsError):
    MSG = 'values already completed, metric must be reinitialized'
