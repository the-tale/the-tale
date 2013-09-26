# coding: utf-8

from rels.django_staff import DjangoEnum


class ACTOR_TYPE(DjangoEnum):
    _records = (('PERSON', 0, u'житель'),
                ('PLACE', 1, u'место'),
                ('MONEY_SPENDING', 2, u'трата денег'))
