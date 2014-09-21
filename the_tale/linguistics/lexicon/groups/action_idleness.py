# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'ACTION_IDLENESS_DESCRIPTION', 60000, u'Описание', LEXICON_GROUP.ACTION_IDLENESS,
        u'Краткая декларация того, что делает герой.',
        [V.HERO]),

        (u'ACTION_IDLENESS_WAITING', 60001, u'Ожидание', LEXICON_GROUP.ACTION_IDLENESS,
        u'Герой занимается каким-нибудь бесполезным делом.',
        [V.HERO]),

        ]
        