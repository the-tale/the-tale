
import smart_imports

smart_imports.all()


V = lexicon_relations.VARIABLE


KEYS = [('ACTION_RELIGION_INCENSE_DESCRIPTION', 160000, 'Описание: курение благовоний', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Краткая декларация того, что делает герой.',
         [V.DATE, V.TIME, V.HERO], None),

        ('ACTION_RELIGION_MEDITATION_DESCRIPTION', 160001, 'Описание: медитация', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Краткая декларация того, что делает герой.',
         [V.DATE, V.TIME, V.HERO], None),

        ('ACTION_RELIGION_PRAY_DESCRIPTION', 160002, 'Описание: молитва', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Краткая декларация того, что делает герой.',
         [V.DATE, V.TIME, V.HERO], None),

        ('ACTION_RELIGION_SACRIFICE_FIRE_DESCRIPTION', 160003, 'Описание: жертвоприношение огнём', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Краткая декларация того, что герой приносит жертву, сжигая останки противника на огне.',
         [V.DATE, V.TIME, V.HERO], None),

        ('ACTION_RELIGION_SACRIFICE_BLOOD_DESCRIPTION', 160020, 'Описание: жертвоприношение кровью', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Краткая декларация того, что герой приносит жертву через ритуал с кровью.',
         [V.DATE, V.TIME, V.HERO], None),

        ('ACTION_RELIGION_SACRIFICE_KNIFE_DESCRIPTION', 160021, 'Описание: жертвоприношение ножом', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Краткая декларация того, что герой приносит жертву, разделывая её на мелкие кусочки.',
         [V.DATE, V.TIME, V.HERO], None),

        ('ACTION_RELIGION_SYMBOLS_STONE_DESCRIPTION', 160004, 'Описание: вырезание символов на камне', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Краткая декларация того, что герой вырезает волшебные руны на камне.',
         [V.DATE, V.TIME, V.HERO], None),

        ('ACTION_RELIGION_SYMBOLS_TREE_DESCRIPTION', 160022, 'Описание: вырезание символов на дереве', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Краткая декларация того, что герой вырезает волшебные руны на дереве.',
         [V.DATE, V.TIME, V.HERO], None),

        ('ACTION_RELIGION_SYMBOLS_GROUND_DESCRIPTION', 160023, 'Описание: вырезание символов на земле', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Краткая декларация того, что герой пишет волшебные руны на земле.',
         [V.DATE, V.TIME, V.HERO], None),

        ('ACTION_RELIGION_INCENSE_PROFIT_RECEIVED', 160005, 'Журнал: Успех курения благовоний', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Окончание курения благовоний и получение награды',
         [V.DATE, V.TIME, V.EXPERIENCE, V.HERO], '+experience#EXP'),

        ('ACTION_RELIGION_MEDITATION_PROFIT_RECEIVED', 160006, 'Журнал: Успех медитации', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Окончание медитации и получение награды',
         [V.DATE, V.TIME, V.EXPERIENCE, V.HERO], '+experience#EXP'),

        ('ACTION_RELIGION_PRAY_PROFIT_RECEIVED', 160007, 'Журнал: Успех молитвы', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Окончание молитвы и получение награды.',
         [V.DATE, V.TIME, V.EXPERIENCE, V.HERO], '+experience#EXP'),

        ('ACTION_RELIGION_SACRIFICE_FIRE_PROFIT_RECEIVED', 160008, 'Журнал: Успех жертвоприношения огнём', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Окончание жертвоприношения с использованием огня и получение награды',
         [V.DATE, V.TIME, V.EXPERIENCE, V.HERO], '+experience#EXP'),

        ('ACTION_RELIGION_SACRIFICE_BLOOD_PROFIT_RECEIVED', 160024, 'Журнал: Усрех жертвоприношения кровью', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Окончание жертвоприношения с использованием крови и получение награды',
         [V.DATE, V.TIME, V.EXPERIENCE, V.HERO], '+experience#EXP'),

        ('ACTION_RELIGION_SACRIFICE_KNIFE_PROFIT_RECEIVED', 160025, 'Журнал: Успех жертвоприношения ножом', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Окончание жертвоприношения с использованием ножа и получение награды',
         [V.DATE, V.TIME, V.EXPERIENCE, V.HERO], '+experience#EXP'),

        ('ACTION_RELIGION_SYMBOLS_STONE_PROFIT_RECEIVED', 160009, 'Журнал: Успех вырезания символов на камне', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Окончание вырезания символов на камне и получение награды',
         [V.DATE, V.TIME, V.EXPERIENCE, V.HERO], '+experience#EXP'),

        ('ACTION_RELIGION_SYMBOLS_TREE_PROFIT_RECEIVED', 160026, 'Журнал: Успех вырезанием символов на дереве', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Окончание вырезания символов на дереве и получение награды',
         [V.DATE, V.TIME, V.EXPERIENCE, V.HERO], '+experience#EXP'),

        ('ACTION_RELIGION_SYMBOLS_GROUND_PROFIT_RECEIVED', 160027, 'Журнал: Успех вырезания символов на земле', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Окончание вырезания символов на земле и получене награды',
         [V.DATE, V.TIME, V.EXPERIENCE, V.HERO], '+experience#EXP'),

        ('ACTION_RELIGION_INCENSE_NO_PROFIT_RECEIVED', 160010, 'Журнал: Неудача курения благовоний', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Окончание курения благовоний.',
         [V.DATE, V.TIME, V.EXPERIENCE, V.HERO], '+experience#EXP'),

        ('ACTION_RELIGION_MEDITATION_NO_PROFIT_RECEIVED', 160011, 'Журнал: Неудача медитации', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Окончание медитации.',
         [V.DATE, V.TIME, V.EXPERIENCE, V.HERO], '+experience#EXP'),

        ('ACTION_RELIGION_PRAY_NO_PROFIT_RECEIVED', 160012, 'Журнал: Неудача молитвы', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Окончание молитвы.',
         [V.DATE, V.TIME, V.EXPERIENCE, V.HERO], '+experience#EXP'),

        ('ACTION_RELIGION_SACRIFICE_FIRE_NO_PROFIT_RECEIVED', 160013, 'Журнал: Неудача жертвоприношения огнём', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Окончание жертвоприношения огнём.',
         [V.DATE, V.TIME, V.EXPERIENCE, V.HERO], '+experience#EXP'),

        ('ACTION_RELIGION_SACRIFICE_BLOOD_NO_PROFIT_RECEIVED', 160028, 'Журнал: Неудача жертвоприношения кровью', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Окончание жертвоприношения кровью.',
         [V.DATE, V.TIME, V.EXPERIENCE, V.HERO], '+experience#EXP'),

        ('ACTION_RELIGION_SACRIFICE_KNIFE_NO_PROFIT_RECEIVED', 160029, 'Журнал: Неудача жертвоприношения ножом', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Окончание жертвоприношения ножом.',
         [V.DATE, V.TIME, V.EXPERIENCE, V.HERO], '+experience#EXP'),

        ('ACTION_RELIGION_SYMBOLS_STONE_NO_PROFIT_RECEIVED', 160014, 'Журнал: Неудача вырезания символов на камне', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Окончание вырезание символов на камне.',
         [V.DATE, V.TIME, V.EXPERIENCE, V.HERO], '+experience#EXP'),

        ('ACTION_RELIGION_SYMBOLS_TREE_NO_PROFIT_RECEIVED', 160030, 'Журнал: Неудача вырезания символов на дереве', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Окончание вырезание символов на деревев.',
         [V.DATE, V.TIME, V.EXPERIENCE, V.HERO], '+experience#EXP'),

        ('ACTION_RELIGION_SYMBOLS_GROUND_NO_PROFIT_RECEIVED', 160031, 'Журнал: Неудача вырезания символов на земле', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Окончание вырезание символов на земле.',
         [V.DATE, V.TIME, V.EXPERIENCE, V.HERO], '+experience#EXP'),

        ('ACTION_RELIGION_INCENSE_START', 160015, 'Журнал: Начало курения благовоний', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Герой начинает курить благовония',
         [V.DATE, V.TIME, V.HERO], None),

        ('ACTION_RELIGION_MEDITATION_START', 160016, 'Журнал: Начало медитации', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Герой приступает к медитации',
         [V.DATE, V.TIME, V.HERO], None),

        ('ACTION_RELIGION_PRAY_START', 160017, 'Журнал: Начало молитвы', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Герой начинает молиться.',
         [V.DATE, V.TIME, V.HERO], None),

        ('ACTION_RELIGION_SACRIFICE_FIRE_START', 160018, 'Журнал: Начало жертвоприношения огнём', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Герой начинает приносить жертву через сжигание останков монстра.',
         [V.DATE, V.TIME, V.HERO], None),

        ('ACTION_RELIGION_SACRIFICE_BLOOD_START', 160032, 'Журнал: Начало жертвоприношения кровью', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Герой начинает приносить жертву кровью монстра.',
         [V.DATE, V.TIME, V.HERO], None),

        ('ACTION_RELIGION_SACRIFICE_KNIFE_START', 160033, 'Журнал: Начало жертвоприношения ножом', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Герой начинает приносить жертву, разделывая останки монстра.',
         [V.DATE, V.TIME, V.HERO], None),

        ('ACTION_RELIGION_SYMBOLS_STONE_START', 160019, 'Журнал: Начало вырезания символов на камне', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Герой начинает вырезать символы на камне',
         [V.DATE, V.TIME, V.HERO], None),

        ('ACTION_RELIGION_SYMBOLS_TREE_START', 160034, 'Журнал: Начало вырезания символов на дереве', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Герой начинает вырезать символы на дереве',
         [V.DATE, V.TIME, V.HERO], None),

        ('ACTION_RELIGION_SYMBOLS_GROUND_START', 160035, 'Журнал: Начало вырезания символов на земле', relations.LEXICON_GROUP.ACTION_RELIGION,
         'Герой начинает вырезать символы на земле',
         [V.DATE, V.TIME, V.HERO], None),

        ]
