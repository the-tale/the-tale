# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

def get_key_records():
    from the_tale.linguistics.lexicon import hero_common

    keys = []
    keys.extend(hero_common.KEYS)

    return keys


class LEXICON_KEY(DjangoEnum):
    group = Column(unique=False)
    description = Column()
    variables = Column(unique=False, no_index=True)

    records = get_key_records()
