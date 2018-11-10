
import smart_imports

smart_imports.all()


V = lexicon_relations.VARIABLE


KEYS = [('META_ACTION_ARENA_PVP_1X1_DESCRIPTION', 320000, 'Описание', relations.LEXICON_GROUP.META_ACTION_ARENA_PVP_1X1,
         'Краткая декларация того, что делает герой.',
         [V.DATE, V.TIME, V.DUELIST_2, V.DUELIST_1], None),

        ('META_ACTION_ARENA_PVP_1X1_KILL', 320001, 'Журнал: Победа', relations.LEXICON_GROUP.META_ACTION_ARENA_PVP_1X1,
         'Один из противников нанёс завершающий удар.',
         [V.DATE, V.TIME, V.KILLER, V.VICTIM], None),

        ('META_ACTION_ARENA_PVP_1X1_START', 320002, 'Журнал: Начало боя', relations.LEXICON_GROUP.META_ACTION_ARENA_PVP_1X1,
         'Герои входят на арену',
         [V.DATE, V.TIME, V.DUELIST_2, V.DUELIST_1], None),

        ]
