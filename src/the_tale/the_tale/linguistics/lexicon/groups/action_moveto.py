# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [('ACTION_MOVETO_DESCRIPTION', 120000, 'Описание', LEXICON_GROUP.ACTION_MOVETO,
        'Краткая декларация того, что делает герой.',
        [V.DESTINATION, V.HERO], None),

        ('ACTION_MOVETO_MOVE', 120001, 'Журнал: Путешествие', LEXICON_GROUP.ACTION_MOVETO,
        'Герой передвигается по дороге в сторону пункта назначения',
        [V.DESTINATION, V.HERO, V.CURRENT_DESTINATION], None),

        ('ACTION_MOVETO_MOVE_LONG_PATH', 120002, 'Журнал: Путешествие, дальняя дорога', LEXICON_GROUP.ACTION_MOVETO,
        'Герой передвигается по дороге в сторону пункта назначения, текущая дорога ведёт не в конечный город и герой хочет использовать во фразе оба города (текущее место назначения и конечное)',
        [V.DESTINATION, V.HERO, V.CURRENT_DESTINATION], None),

        ('ACTION_MOVETO_PICKED_UP_IN_ROAD', 120003, 'Журнал: Подвезли караваном', LEXICON_GROUP.ACTION_MOVETO,
        'Героя подвёз встречный караван или что-то похожее',
        [V.DESTINATION, V.HERO], None),

        ('ACTION_MOVETO_START', 120004, 'Журнал: Начало путешествия', LEXICON_GROUP.ACTION_MOVETO,
        'Герой выходит из начальной точки путешествия',
        [V.DESTINATION, V.HERO], None),

        ]
