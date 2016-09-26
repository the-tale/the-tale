# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [('ACTION_IDLENESS_DESCRIPTION', 60000, 'Описание', LEXICON_GROUP.ACTION_IDLENESS,
        'Краткая декларация того, что делает герой.',
        [V.HERO], None),

        ('ACTION_IDLENESS_WAITING', 60001, 'Журнал: Ожидание', LEXICON_GROUP.ACTION_IDLENESS,
        'Герой занимается каким-нибудь бесполезным делом.',
        [V.HERO], None),

        ]
