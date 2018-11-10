
import smart_imports

smart_imports.all()


V = lexicon_relations.VARIABLE


KEYS = [('ACTION_MOVETO_DESCRIPTION', 120000, 'Описание', relations.LEXICON_GROUP.ACTION_MOVETO,
         'Краткая декларация того, что делает герой.',
         [V.DATE, V.TIME, V.DESTINATION, V.HERO], None),

        ('ACTION_MOVETO_MOVE', 120001, 'Журнал: Путешествие', relations.LEXICON_GROUP.ACTION_MOVETO,
         'Герой передвигается по дороге в сторону пункта назначения',
         [V.DATE, V.TIME, V.DESTINATION, V.HERO, V.CURRENT_DESTINATION], None),

        ('ACTION_MOVETO_MOVE_LONG_PATH', 120002, 'Журнал: Путешествие, дальняя дорога', relations.LEXICON_GROUP.ACTION_MOVETO,
         'Герой передвигается по дороге в сторону пункта назначения, текущая дорога ведёт не в конечный город и герой хочет использовать во фразе оба города (текущее место назначения и конечное)',
         [V.DATE, V.TIME, V.DESTINATION, V.HERO, V.CURRENT_DESTINATION], None),

        ('ACTION_MOVETO_PICKED_UP_IN_ROAD', 120003, 'Журнал: Подвезли караваном', relations.LEXICON_GROUP.ACTION_MOVETO,
         'Героя подвёз встречный караван или что-то похожее',
         [V.DATE, V.TIME, V.DESTINATION, V.HERO], None),

        ('ACTION_MOVETO_START', 120004, 'Журнал: Начало путешествия', relations.LEXICON_GROUP.ACTION_MOVETO,
         'Герой выходит из начальной точки путешествия',
         [V.DATE, V.TIME, V.DESTINATION, V.HERO], None),

        ]
