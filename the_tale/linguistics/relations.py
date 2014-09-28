# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from utg import relations as utg_relations

def word_type_record(name):
    utg_type = utg_relations.WORD_TYPE.index_name[name]
    return (name,
            utg_type.value,
            utg_type.text,
            utg_type)

class ALLOWED_WORD_TYPE(DjangoEnum):
    utg_type = Column()

    records = ( word_type_record('NOUN'),
                word_type_record('ADJECTIVE'),
                word_type_record('PRONOUN'),
                word_type_record('VERB'),
                word_type_record('PARTICIPLE'),
                word_type_record('SHORT_ADJECTIVE'),
                word_type_record('SHORT_PARTICIPLE') )


class WORD_STATE(DjangoEnum):
    records = ( ('ON_REVIEW', 0, u'на рассмотрении'),
                ('IN_GAME', 1, u'в игре'))


class WORD_BLOCK_BASE(DjangoEnum):
    schema = Column()

    records = ( ('NC', 0, u'число-падеж', (utg_relations.NUMBER, utg_relations.CASE)),
                ('NCG', 1, u'число-падеж-род', (utg_relations.NUMBER, utg_relations.CASE, utg_relations.GENDER)),
                ('NP', 2, u'число-лицо', (utg_relations.NUMBER, utg_relations.PERSON)),
                ('NPG', 3, u'число-лицо-род', (utg_relations.NUMBER, utg_relations.PERSON, utg_relations.GENDER)),
                ('SINGLE', 4, u'одна форма', ()),
                ('NG', 5, u'число-род', (utg_relations.NUMBER, utg_relations.GENDER)),
                ('C', 6, u'падеж', (utg_relations.CASE, )),  )



class TEMPLATE_STATE(DjangoEnum):
    records = ( ('ON_REVIEW', 0, u'на рассмотрении'),
                ('IN_GAME', 1, u'в игре'))
