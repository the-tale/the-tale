# coding: utf-8

from rels.django import DjangoEnum


class PHRASE_CANDIDATE_STATE(DjangoEnum):
    records = ( ('IN_QUEUE', 0, u'ожидает проверку'),
                ('REMOVED', 1, u'удалена'),
                ('APPROVED', 2, u'одобрена'),
                ('ADDED', 3, u'добавлена') )
