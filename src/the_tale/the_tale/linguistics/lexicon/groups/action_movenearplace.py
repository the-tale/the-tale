# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [('ACTION_MOVENEARPLACE_DESCRIPTION', 100000, 'Описание', LEXICON_GROUP.ACTION_MOVENEARPLACE,
        'Краткая декларация того, что делает герой.',
        [V.DATE, V.HERO, V.PLACE], None),

        ('ACTION_MOVENEARPLACE_WALK', 100001, 'Журнал: Путешествие', LEXICON_GROUP.ACTION_MOVENEARPLACE,
        'Герой путешествует.',
        [V.DATE, V.HERO, V.PLACE], None),

        ]
