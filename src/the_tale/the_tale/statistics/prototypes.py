# coding: utf-8
import datetime

from the_tale.common.utils.prototypes import BasePrototype

from the_tale.statistics.models import Record
from the_tale.statistics import exceptions
from the_tale.statistics import relations


class RecordPrototype(BasePrototype):
    _model_class = Record
    _readonly = ('id', 'date', 'type', 'value_int', 'value_float')
    _bidirectional = ()
    _get_by = ()


    @classmethod
    def create(cls, type, date, value_int=None, value_float=None):

        if value_int is None and value_float is None:
            raise exceptions.ValueNotSpecifiedError()

        if value_int is None:
            if type.value_type.is_INT:
                raise exceptions.ValueNotSpecifiedForTypeError(type=type)
            value_int = int(value_float)

        if value_float is None:
            if type.value_type.is_FLOAT:
                raise exceptions.ValueNotSpecifiedForTypeError(type=type)
            value_float = float(value_int)

        model = cls._model_class.objects.create(date=date,
                                                type=type,
                                                value_int=value_int,
                                                value_float=value_float)

        return cls(model=model)


    @classmethod
    def remove_by_type(cls, type):
        cls._db_filter(type=type).delete()


    @classmethod
    def select(cls, type, date_from, date_to):

        if date_to < date_from:
            raise exceptions.InvertedDateIntervalError(date_to=date_to, date_from=date_from)

        query = cls._db_filter(type=type, date__gte=date_from, date__lte=date_to).order_by('date')

        if type.value_type.is_INT:
            return list(query.values_list('date', 'value_int'))

        if type.value_type.is_FLOAT:
            return list(query.values_list('date', 'value_float'))

    @classmethod
    def select_values(cls, *argv, **kwargs):
        data = cls.select(*argv, **kwargs)
        return zip(*data)[1]

    @classmethod
    def select_for_js(cls, type, date_from, date_to):
        data = cls.select(type=type, date_from=date_from, date_to=date_to)
        return [(date.date().isoformat(), value) for date, value in data]


    @classmethod
    def get_js_data(cls):
        return {record.value: RecordPrototype.select_for_js(record,
                                                            date_from=datetime.datetime.min,
                                                            date_to=datetime.datetime.now()) for record in relations.RECORD_TYPE.records}
