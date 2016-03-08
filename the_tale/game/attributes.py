# coding: utf-8
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


def attr(name, value, text, default=lambda: 0, type=ATTRIBUTE_TYPE.AGGREGATED, order=1, description=None, apply=operator.add):
    return (name, value, text, default, type, order, (description if description is not None else text), apply)


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
            return {name: getattr(self, name) for name in self.__slots__}

        @classmethod
        def deserialize(cls, data):
            return cls(**data)

        def reset(self):
            for attribute in ATTRIBUTES.records:
                if attribute.type.is_CALCULATED:
                    continue
                setattr(self, attribute.name.lower(), attribute.default())

    return Attributes
