# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'ACTION_MOVENEARPLACE_DESCRIPTION', 100000, u'Описание', LEXICON_GROUP.ACTION_MOVENEARPLACE,
        u'Краткая декларация того, что делает герой.',
        [V.HERO, V.PLACE]),

        (u'ACTION_MOVENEARPLACE_WALK', 100001, u'Журнал: Путешествие', LEXICON_GROUP.ACTION_MOVENEARPLACE,
        u'Герой путешествует.',
        [V.HERO, V.PLACE]),

        ]
