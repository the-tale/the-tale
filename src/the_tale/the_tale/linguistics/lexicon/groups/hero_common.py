# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [('HERO_COMMON_JOURNAL_LEVEL_UP', 300005, 'Журнал: Получение уровня', LEXICON_GROUP.HERO_COMMON,
        'Герой получает уровень.',
        [V.HERO, V.LEVEL], None),

        ('HERO_COMMON_JOURNAL_RETURN_CHILD_GIFT', 300006, 'Журнал: Детский подарок вернулся к ребёнку', LEXICON_GROUP.HERO_COMMON,
        'Найденный детский подарок пропадает из рюкзака и возвращается к ребёнку.',
        [V.HERO, V.ARTIFACT], None),
        ]
