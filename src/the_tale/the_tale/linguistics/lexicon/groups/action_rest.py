# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [('ACTION_REST_DESCRIPTION', 180000, 'Описание', LEXICON_GROUP.ACTION_REST,
        'Краткая декларация того, что делает герой.',
        [V.DATE, V.HERO], None),

        ('ACTION_REST_RESRING', 180001, 'Журнал: Отдых', LEXICON_GROUP.ACTION_REST,
        'Герой лечится и восстанавливает немного здоровья.',
        [V.DATE, V.HERO, V.HEALTH], 'hero#N +health#HP'),

        ('ACTION_REST_START', 180002, 'Журнал: Начало', LEXICON_GROUP.ACTION_REST,
        'Герой начинает лечиться.',
        [V.DATE, V.HERO], None),

        ]
