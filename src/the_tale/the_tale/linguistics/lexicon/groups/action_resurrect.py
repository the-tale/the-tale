# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [('ACTION_RESURRECT_DESCRIPTION', 200000, 'Описание', LEXICON_GROUP.ACTION_RESURRECT,
        'Краткая декларация того, что делает герой.',
        [V.HERO], None),

        ('ACTION_RESURRECT_FINISH', 200001, 'Журнал: Воскрешение закончено', LEXICON_GROUP.ACTION_RESURRECT,
        'Герой закончил воскресать.',
        [V.HERO], None),

        ('ACTION_RESURRECT_RESURRECTING', 200002, 'Журнал: Идёт воскрешение', LEXICON_GROUP.ACTION_RESURRECT,
        'Хранитель приводит героя в чувства.',
        [V.HERO], None),

        ('ACTION_RESURRECT_START', 200003, 'Журнал: Начало воскрешения', LEXICON_GROUP.ACTION_RESURRECT,
        'Герой только что умер и начинается его воскрешение.',
        [V.HERO], None),

        ]
