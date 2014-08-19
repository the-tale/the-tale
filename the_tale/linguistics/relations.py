# coding: utf-8

from rels.django import DjangoEnum


class WORD_STATE(DjangoEnum):
    records = ( ('ON_REVIEW', 0, u'на рассмотрении'),
                ('IN_GAME', 1, u'в игре'))
