# coding: utf-8

from rels.django import DjangoEnum


class EMAILED_STATE(DjangoEnum):
    records = ( ('EMAILED', 0, u'письма отправлены'),
                ('NOT_EMAILED', 1, u'письма не отправлены'),
                ('DISABLED', 2, u'отправка запрещена') )
