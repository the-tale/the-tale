# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from utg import relations as utg_relations


class WORD_STATE(DjangoEnum):
    records = ( ('ON_REVIEW', 0, u'на рассмотрении'),
                ('IN_GAME', 1, u'в игре'))


class WORD_BLOCK_BASE(DjangoEnum):
    schema = Column()

    records = ( ('NC', 0, u'число-падеж', (utg_relations.NUMBER, utg_relations.CASE)),
                ('NCG', 1, u'число-падеж-род', (utg_relations.NUMBER, utg_relations.CASE, utg_relations.GENDER)),
                ('TP', 2, u'время-лицо', (utg_relations.TIME, utg_relations.PERSON)),
                ('SINGLE', 3, u'одна форма', ())  )
