

import smart_imports

smart_imports.all()


V = lexicon_relations.VARIABLE


KEYS = [('ACTION_REST_DESCRIPTION', 180000, 'Описание', relations.LEXICON_GROUP.ACTION_REST,
         'Краткая декларация того, что делает герой.',
         [V.DATE, V.TIME, V.HERO], None),

        ('ACTION_REST_RESRING', 180001, 'Журнал: Отдых', relations.LEXICON_GROUP.ACTION_REST,
         'Герой лечится и восстанавливает немного здоровья.',
         [V.DATE, V.TIME, V.HERO, V.HEALTH], 'hero#N +health#HP'),

        ('ACTION_REST_START', 180002, 'Журнал: Начало', relations.LEXICON_GROUP.ACTION_REST,
         'Герой начинает лечиться.',
         [V.DATE, V.TIME, V.HERO], None),

        ]
