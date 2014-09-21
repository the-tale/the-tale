# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'HERO_COMMON_DIARY_CREATE', 300000, u'Создание героя', LEXICON_GROUP.HERO_COMMON,
        u'Первая запись героя в дневнике.',
        [V.HERO]),

        (u'HERO_COMMON_JOURNAL_CREATE_1', 300001, u'Создание героя, фраза 1', LEXICON_GROUP.HERO_COMMON,
        u'фраза 1 в журнале героя — первая мысль о геройстве.',
        [V.HERO]),

        (u'HERO_COMMON_JOURNAL_CREATE_2', 300002, u'Создание героя, фраза 2', LEXICON_GROUP.HERO_COMMON,
        u'фраза 2 в журнале героя — мысль о будущем.',
        [V.HERO]),

        (u'HERO_COMMON_JOURNAL_CREATE_3', 300003, u'Создание героя, фраза 3', LEXICON_GROUP.HERO_COMMON,
        u'фраза 3 в журнале героя — мысль о героях.',
        [V.HERO]),

        (u'HERO_COMMON_JOURNAL_CREATE_4', 300004, u'Создание героя, фраза 4', LEXICON_GROUP.HERO_COMMON,
        u'фраза 4 в журнале героя — мысль о текущей ситуации.',
        [V.HERO]),

        (u'HERO_COMMON_JOURNAL_LEVEL_UP', 300005, u'Получение уровня', LEXICON_GROUP.HERO_COMMON,
        u'Герой получает уровень.',
        [V.HERO, V.LEVEL]),

        ]
        