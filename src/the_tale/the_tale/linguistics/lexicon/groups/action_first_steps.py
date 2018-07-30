
import smart_imports

smart_imports.all()


V = lexicon_relations.VARIABLE


KEYS = [('ACTION_FIRST_STEPS_INITIATION_DIARY', 640000, 'Дневник: первая запись в дневник', relations.LEXICON_GROUP.ACTION_FIRST_STEPS,
         'Первая запись героя в дневнике.',
         [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_FIRST_STEPS_INITIATION', 640001, 'Журнал: первая мысль о геройстве', relations.LEXICON_GROUP.ACTION_FIRST_STEPS,
         'фраза 1 в журнале героя — первая мысль о геройстве.',
         [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_FIRST_STEPS_FUTURE', 640002, 'Журнал: размышление о будущем', relations.LEXICON_GROUP.ACTION_FIRST_STEPS,
         'фраза 2 в журнале героя — мысль о будущем.',
         [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_FIRST_STEPS_HEROES', 640003, 'Журнал: размышление о героях', relations.LEXICON_GROUP.ACTION_FIRST_STEPS,
         'фраза 3 в журнале героя — мысль о героях.',
         [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_FIRST_STEPS_NOW', 640004, 'Журнал: размышления о текущей ситуации', relations.LEXICON_GROUP.ACTION_FIRST_STEPS,
         'фраза 4 в журнале героя — мысль о текущей ситуации.',
         [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_FIRST_STEPS_DESCRIPTION', 640005, 'Описание', relations.LEXICON_GROUP.ACTION_FIRST_STEPS,
         'Краткая декларация того, что делает герой.',
         [V.DATE, V.TIME, V.HERO, V.PLACE], None),
        ]
