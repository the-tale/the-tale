# coding: utf-8

from rels.django import DjangoEnum


class POST_STATE(DjangoEnum):
    records = (('NOT_MODERATED', 0, u'не проверен'),
                ('ACCEPTED', 1, u'принят'),
                ('DECLINED', 2, u'отклонён'), )
