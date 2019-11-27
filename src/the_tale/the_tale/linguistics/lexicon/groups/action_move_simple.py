
import smart_imports

smart_imports.all()


V = lexicon_relations.VARIABLE


KEYS = [('ACTION_MOVE_SIMPLE_TO_DESCRIPTION', 120000, 'Описание: герой движется в город', relations.LEXICON_GROUP.ACTION_MOVE_SIMPLE_TO,
         'Краткая декларация того, что делает герой, когда он движется в город.',
         [V.DATE, V.TIME, V.DESTINATION, V.HERO], None),

        ('ACTION_MOVE_SIMPLE_TO_MOVE', 120001, 'Журнал: Путешествие по дороге в город', relations.LEXICON_GROUP.ACTION_MOVE_SIMPLE_TO,
         'Герой передвигается по дороге в сторону пункта назначения',
         [V.DATE, V.TIME, V.DESTINATION, V.HERO, V.CURRENT_DESTINATION], None),

        ('ACTION_MOVE_SIMPLE_TO_MOVE_LONG_PATH', 120002, 'Журнал: Путешествие, дальняя дорога в город', relations.LEXICON_GROUP.ACTION_MOVE_SIMPLE_TO,
         'Герой передвигается по дороге в сторону пункта назначения, текущая дорога ведёт не в конечный город и герой хочет использовать во фразе оба города (текущее место назначения и конечное)',
         [V.DATE, V.TIME, V.DESTINATION, V.HERO, V.CURRENT_DESTINATION], None),

        ('ACTION_MOVE_SIMPLE_TO_PICKED_UP_IN_ROAD', 120003, 'Журнал: Подвезли караваном в город', relations.LEXICON_GROUP.ACTION_MOVE_SIMPLE_TO,
         'Героя подвёз встречный караван или что-то похожее',
         [V.DATE, V.TIME, V.DESTINATION, V.HERO], None),

        ('ACTION_MOVE_SIMPLE_TO_START', 120004, 'Журнал: Начало путешествия в город', relations.LEXICON_GROUP.ACTION_MOVE_SIMPLE_TO,
         'Герой выходит из начального города и идёт в конечный',
         [V.DATE, V.TIME, V.DESTINATION, V.HERO], None),

        ('ACTION_MOVE_SIMPLE_NEAR_DESCRIPTION', 100000, 'Описание: герой движется не в город', relations.LEXICON_GROUP.ACTION_MOVE_SIMPLE_NEAR,
         'Краткая декларация того, что делает герой, когда он движется не в город.',
         [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_MOVE_SIMPLE_NEAR_WALK', 100001, 'Журнал: Путешествие не по дороге или не в город', relations.LEXICON_GROUP.ACTION_MOVE_SIMPLE_NEAR,
         'Герой путешествует, не по дороге или не в город.',
         [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_MOVE_SIMPLE_TO_TELEPORT_WITH_CLAN', 120005, 'Журнал: быстрое путешествие с помощью гильдии', relations.LEXICON_GROUP.ACTION_MOVE_SIMPLE_TO,
         'Гильдия предоставляет герою безопасный путь до следующего города. Герой «телепортируется» туда.',
         [V.DATE, V.TIME, V.HERO, V.CLAN, V.CURRENT_DESTINATION], None),

        ]
