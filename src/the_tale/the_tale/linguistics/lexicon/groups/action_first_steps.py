# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP


KEYS = [('ACTION_FIRST_STEPS_INITIATION_DIARY', 640000, 'Дневник: первая запись в дневник', LEXICON_GROUP.ACTION_FIRST_STEPS,
        'Первая запись героя в дневнике.',
        [V.HERO, V.PLACE], None),

        ('ACTION_FIRST_STEPS_INITIATION', 640001, 'Журнал: первая мысль о геройстве', LEXICON_GROUP.ACTION_FIRST_STEPS,
        'фраза 1 в журнале героя — первая мысль о геройстве.',
        [V.HERO, V.PLACE], None),

        ('ACTION_FIRST_STEPS_FUTURE', 640002, 'Журнал: размышление о будущем', LEXICON_GROUP.ACTION_FIRST_STEPS,
        'фраза 2 в журнале героя — мысль о будущем.',
        [V.HERO, V.PLACE], None),

        ('ACTION_FIRST_STEPS_HEROES', 640003, 'Журнал: размышление о героя', LEXICON_GROUP.ACTION_FIRST_STEPS,
        'фраза 3 в журнале героя — мысль о героях.',
        [V.HERO, V.PLACE], None),

        ('ACTION_FIRST_STEPS_NOW', 640004, 'Журнал: размышления о текущей ситуации', LEXICON_GROUP.ACTION_FIRST_STEPS,
        'фраза 4 в журнале героя — мысль о текущей ситуации.',
        [V.HERO, V.PLACE], None),

        ('ACTION_FIRST_STEPS_DESCRIPTION', 640005, 'Описание', LEXICON_GROUP.ACTION_FIRST_STEPS,
        'Краткая декларация того, что делает герой.',
        [V.HERO, V.PLACE], None),
        ]
