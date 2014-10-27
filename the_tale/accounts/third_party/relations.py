# coding: utf-8

from rels.django import DjangoEnum


class ACCESS_TOKEN_STATE(DjangoEnum):
    records = ( ('UNACCEPTED', 0, u'неизвестен'),
                ('ACCEPTED', 1, u'разрешено') )
