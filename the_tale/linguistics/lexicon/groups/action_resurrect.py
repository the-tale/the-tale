# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'ACTION_RESURRECT_DESCRIPTION', 200000, u'Описание', LEXICON_GROUP.ACTION_RESURRECT,
        u'Краткая декларация того, что делает герой.',
        [V.HERO]),

        (u'ACTION_RESURRECT_FINISH', 200001, u'Журнал: Воскрешение закончено', LEXICON_GROUP.ACTION_RESURRECT,
        u'Герой закончил воскресать.',
        [V.HERO]),

        (u'ACTION_RESURRECT_RESURRECTING', 200002, u'Журнал: Идёт воскрешение', LEXICON_GROUP.ACTION_RESURRECT,
        u'Хранитель приводит героя в чувства.',
        [V.HERO]),

        (u'ACTION_RESURRECT_START', 200003, u'Журнал: Начало воскрешения', LEXICON_GROUP.ACTION_RESURRECT,
        u'Герой только что умер и начинается его воскрешение.',
        [V.HERO]),

        ]
