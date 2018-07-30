
import smart_imports

smart_imports.all()


V = lexicon_relations.VARIABLE


KEYS = [('ACTION_RESURRECT_DESCRIPTION', 200000, 'Описание', relations.LEXICON_GROUP.ACTION_RESURRECT,
         'Краткая декларация того, что делает герой.',
         [V.DATE, V.TIME, V.HERO], None),

        ('ACTION_RESURRECT_FINISH', 200001, 'Журнал: Воскрешение закончено', relations.LEXICON_GROUP.ACTION_RESURRECT,
         'Герой закончил воскресать.',
         [V.DATE, V.TIME, V.HERO], None),

        ('ACTION_RESURRECT_RESURRECTING', 200002, 'Журнал: Идёт воскрешение', relations.LEXICON_GROUP.ACTION_RESURRECT,
         'Хранитель приводит героя в чувства.',
         [V.DATE, V.TIME, V.HERO], None),

        ('ACTION_RESURRECT_START', 200003, 'Журнал: Начало воскрешения', relations.LEXICON_GROUP.ACTION_RESURRECT,
         'Герой только что умер и начинается его воскрешение.',
         [V.DATE, V.TIME, V.HERO], None),

        ]
