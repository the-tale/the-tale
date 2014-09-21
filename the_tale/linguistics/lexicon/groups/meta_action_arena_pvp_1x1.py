# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'META_ACTION_ARENA_PVP_1X1_DESCRIPTION', 320000, u'Описание', LEXICON_GROUP.META_ACTION_ARENA_PVP_1X1,
        u'Краткая декларация того, что делает герой.',
        [V.HERO]),

        (u'META_ACTION_ARENA_PVP_1X1_DIARY_KILL', 320001, u'Дневник: Победа', LEXICON_GROUP.META_ACTION_ARENA_PVP_1X1,
        u'Один из противников нанёс завершающий удар.',
        [V.KILLER, V.VICTIM]),

        (u'META_ACTION_ARENA_PVP_1X1_START', 320002, u'Начало боя', LEXICON_GROUP.META_ACTION_ARENA_PVP_1X1,
        u'Герои входят на арену',
        [V.DUELIST_2, V.DUELIST_1]),

        ]
        