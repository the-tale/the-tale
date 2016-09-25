# coding: utf-8

from rels import Column
from rels.django import DjangoEnum


class PAYMENT_GROUPS(DjangoEnum):
    top_border = Column()

    records = ( ('INT_1', 0, u'0 … 600', 500),
                ('INT_2', 1, u'600 … 1100', 1100),
                ('INT_3', 2, u'1100 … 2600', 2600),
                ('INT_4', 3, u'2600 … 10100', 10000),
                ('INT_5', 4, u'10100 … 9999999', 9999999))
