# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [('HERO_COMMON_DIARY_CREATE', 300000, 'Дневник: Создание героя', LEXICON_GROUP.HERO_COMMON,
        'Первая запись героя в дневнике.',
        [V.HERO], None),

        ('HERO_COMMON_JOURNAL_CREATE_1', 300001, 'Журнал: Создание героя, фраза 1', LEXICON_GROUP.HERO_COMMON,
        'фраза 1 в журнале героя — первая мысль о геройстве.',
        [V.HERO], None),

        ('HERO_COMMON_JOURNAL_CREATE_2', 300002, 'Журнал: Создание героя, фраза 2', LEXICON_GROUP.HERO_COMMON,
        'фраза 2 в журнале героя — мысль о будущем.',
        [V.HERO], None),

        ('HERO_COMMON_JOURNAL_CREATE_3', 300003, 'Журнал: Создание героя, фраза 3', LEXICON_GROUP.HERO_COMMON,
        'фраза 3 в журнале героя — мысль о героях.',
        [V.HERO], None),

        ('HERO_COMMON_JOURNAL_CREATE_4', 300004, 'Журнал: Создание героя, фраза 4', LEXICON_GROUP.HERO_COMMON,
        'фраза 4 в журнале героя — мысль о текущей ситуации.',
        [V.HERO], None),

        ('HERO_COMMON_JOURNAL_LEVEL_UP', 300005, 'Журнал: Получение уровня', LEXICON_GROUP.HERO_COMMON,
        'Герой получает уровень.',
        [V.HERO, V.LEVEL], None),

        ('HERO_COMMON_JOURNAL_RETURN_CHILD_GIFT', 300006, 'Журнал: Детский подарок вернулся к ребёнку', LEXICON_GROUP.HERO_COMMON,
        'Найденный детский подарок пропадает из рюкзака и возвращается к ребёнку.',
        [V.HERO, V.ARTIFACT], None),
        ]
