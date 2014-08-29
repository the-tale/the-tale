# coding: utf-8

from rels import Column
from rels.django import DjangoEnum


class VARIABLE(DjangoEnum):
    test_values = Column(unique=False, no_index=True)

    records = ( ('HERO', 'hero', u'герой', [u'призрак', u'привидение', u'русалка']),
                ('LEVEL', 'level', u'уровень', [13]), )


class LEXICON_GROUP(DjangoEnum):
    index_group = Column()
    description = Column()

    records = ( ('HERO_COMMON', 0, u'Общие сообщения, относящиеся к герою', 0,
                 u'Сообщения, относящиеся к герою и не вошедшие в другие модули.'), )
