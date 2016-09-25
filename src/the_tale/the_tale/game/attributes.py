# coding: utf-8
import numbers
import operator

from rels import Column
from rels.django import DjangoEnum


class ATTRIBUTE_TYPE(DjangoEnum):
    records = ( ('AGGREGATED', 0, u'аггрегируемый'),
                ('CALCULATED', 1, u'вычисляемый'))

class ATTRIBUTE(DjangoEnum):
    default = Column(unique=False, primary=False, single_type=False)
    type = Column(unique=False, primary=False)
    order = Column(unique=False, primary=False)
    description = Column(primary=False)
    apply = Column(primary=False, unique=False, single_type=False)
    verbose_units = Column(unique=False, primary=False)
    serializer = Column(unique=False)
    deserializer = Column(unique=False)
    formatter = Column(unique=False, single_type=False)


def attr(name, value, text, default=lambda: 0, type=ATTRIBUTE_TYPE.AGGREGATED, order=1, description=None, apply=operator.add, verbose_units=u'', serializer=lambda x: x, deserializer=lambda x: x, formatter=lambda x: x):
    return (name, value, text, default, type, order, (description if description is not None else text), apply, verbose_units, serializer, deserializer, formatter)


def create_attributes_class(ATTRIBUTES):

    class Attributes(object):
        __slots__ = tuple([record.name.lower() for record in ATTRIBUTES.records])

        def __init__(self, **kwargs):
            for name, value in kwargs.iteritems():
                setattr(self, name, value)

            for attribute in ATTRIBUTES.records:
                if not hasattr(self, attribute.name.lower()):
                    setattr(self, attribute.name.lower(), attribute.default())

        def serialize(self):
            return {record.name.lower(): record.serializer(getattr(self, record.name.lower())) for record in ATTRIBUTES.records}

        @classmethod
        def deserialize(cls, data):
            return cls(**{k: ATTRIBUTES.index_name[k.upper()].deserializer(v) for k,v in data.iteritems() if k.upper() in ATTRIBUTES.index_name})

        def reset(self):
            for attribute in ATTRIBUTES.records:
                if attribute.type.is_CALCULATED:
                    continue
                setattr(self, attribute.name.lower(), attribute.default())

        def attributes_by_name(self):
            return sorted(ATTRIBUTES.records, key=lambda x: x.text)

    return Attributes


def attributes_info(effects, attrs, relation):
    attributes = []

    for record in relation.records:
        value = getattr(attrs, record.name.lower())
        if not isinstance(value, (numbers.Number, basestring)):
            value = None
        attributes.append({"id": record.value, "value": value})

    return {'effects': [effect.ui_info() for effect in effects],
            'attributes': attributes}



def percents_formatter(value):
    return '%.2f' % round(value*100, 2)

def float_formatter(value):
    return '%.2f' % round(value, 2)
