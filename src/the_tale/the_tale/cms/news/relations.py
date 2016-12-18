# coding: utf-8

from rels.django import DjangoEnum


class EMAILED_STATE(DjangoEnum):
    records = ( ('EMAILED', 0, 'письма отправлены'),
                ('NOT_EMAILED', 1, 'письма не отправлены'),
                ('DISABLED', 2, 'отправка запрещена') )
