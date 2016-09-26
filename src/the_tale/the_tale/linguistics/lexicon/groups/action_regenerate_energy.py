# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [('ACTION_REGENERATE_ENERGY_INCENSE_DESCRIPTION', 160000, 'Описание: курение благовоний', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Краткая декларация того, что делает герой.',
         [V.HERO], None),

        ('ACTION_REGENERATE_ENERGY_MEDITATION_DESCRIPTION', 160001, 'Описание: медитация', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Краткая декларация того, что делает герой.',
         [V.HERO], None),

        ('ACTION_REGENERATE_ENERGY_PRAY_DESCRIPTION', 160002, 'Описание: молитва', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Краткая декларация того, что делает герой.',
         [V.HERO], None),

        ('ACTION_REGENERATE_ENERGY_SACRIFICE_FIRE_DESCRIPTION', 160003, 'Описание: жертвоприношение огнём', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Краткая декларация того, что герой приносит жертву, сжигая останки противника на огне.',
         [V.HERO], None),

        ('ACTION_REGENERATE_ENERGY_SACRIFICE_BLOOD_DESCRIPTION', 160020, 'Описание: жертвоприношение кровью', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Краткая декларация того, что герой приносит жертву через ритуал с кровью.',
         [V.HERO], None),

        ('ACTION_REGENERATE_ENERGY_SACRIFICE_KNIFE_DESCRIPTION', 160021, 'Описание: жертвоприношение ножом', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Краткая декларация того, что герой приносит жертву, разделывая её на мелкие кусочки.',
         [V.HERO], None),

        ('ACTION_REGENERATE_ENERGY_SYMBOLS_STONE_DESCRIPTION', 160004, 'Описание: вырезание символов на камне', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Краткая декларация того, что герой вырезает волшебные руны на камне.',
         [V.HERO], None),

        ('ACTION_REGENERATE_ENERGY_SYMBOLS_TREE_DESCRIPTION', 160022, 'Описание: вырезание символов на дереве', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Краткая декларация того, что герой вырезает волшебные руны на дереве.',
         [V.HERO], None),

        ('ACTION_REGENERATE_ENERGY_SYMBOLS_GROUND_DESCRIPTION', 160023, 'Описание: вырезание символов на земле', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Краткая декларация того, что герой пишет волшебные руны на земле.',
         [V.HERO], None),

        ('ACTION_REGENERATE_ENERGY_INCENSE_ENERGY_RECEIVED', 160005, 'Журнал: Получение энергии курением благовоний', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Окончание курения благовоний и восстановление части энергии',
         [V.ENERGY, V.HERO], '+energy#EN'),

        ('ACTION_REGENERATE_ENERGY_MEDITATION_ENERGY_RECEIVED', 160006, 'Журнал: Получение энергии медитацией', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Окончание медитации и восстановление части энергии',
         [V.ENERGY, V.HERO], '+energy#EN'),

        ('ACTION_REGENERATE_ENERGY_PRAY_ENERGY_RECEIVED', 160007, 'Журнал: Получение энергии молитвой', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Окончание молитвы и восстановление части энергии.',
         [V.ENERGY, V.HERO], '+energy#EN'),

        ('ACTION_REGENERATE_ENERGY_SACRIFICE_FIRE_ENERGY_RECEIVED', 160008, 'Журнал: Получение энергии жертвоприношением огнём', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Окончание жертвоприношения с использованием огня и восстановление части энергии',
         [V.ENERGY, V.HERO], '+energy#EN'),

        ('ACTION_REGENERATE_ENERGY_SACRIFICE_BLOOD_ENERGY_RECEIVED', 160024, 'Журнал: Получение энергии жертвоприношением кровью', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Окончание жертвоприношения с использованием крови и восстановление части энергии',
         [V.ENERGY, V.HERO], '+energy#EN'),

        ('ACTION_REGENERATE_ENERGY_SACRIFICE_KNIFE_ENERGY_RECEIVED', 160025, 'Журнал: Получение энергии жертвоприношением ножом', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Окончание жертвоприношения с использованием ножа и восстановление части энергии',
         [V.ENERGY, V.HERO], '+energy#EN'),

        ('ACTION_REGENERATE_ENERGY_SYMBOLS_STONE_ENERGY_RECEIVED', 160009, 'Журнал: Получение энергии вырезанием символов на камне', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Окончание вырезания символов на камне и восстановление части энергии',
        [V.ENERGY, V.HERO], '+energy#EN'),

        ('ACTION_REGENERATE_ENERGY_SYMBOLS_TREE_ENERGY_RECEIVED', 160026, 'Журнал: Получение энергии вырезанием символов на дереве', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Окончание вырезания символов на дереве и восстановление части энергии',
         [V.ENERGY, V.HERO], '+energy#EN'),

        ('ACTION_REGENERATE_ENERGY_SYMBOLS_GROUND_ENERGY_RECEIVED', 160027, 'Журнал: Получение энергии вырезанием символов на земле', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Окончание вырезания символов на земле и восстановление части энергии',
         [V.ENERGY, V.HERO], '+energy#EN'),

        ('ACTION_REGENERATE_ENERGY_INCENSE_NO_ENERGY_RECEIVED', 160010, 'Журнал: Энергия не восстановлена курением благовоний', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Окончание курения благовоний.',
         [V.ENERGY, V.HERO], '+energy#EN'),

        ('ACTION_REGENERATE_ENERGY_MEDITATION_NO_ENERGY_RECEIVED', 160011, 'Журнал: Энергия не восстановлена медитацией', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Окончание медитации.',
         [V.ENERGY, V.HERO], '+energy#EN'),

        ('ACTION_REGENERATE_ENERGY_PRAY_NO_ENERGY_RECEIVED', 160012, 'Журнал: Энергия не восстановлена молитвой', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Окончание молитвы.',
         [V.ENERGY, V.HERO], '+energy#EN'),

        ('ACTION_REGENERATE_ENERGY_SACRIFICE_FIRE_NO_ENERGY_RECEIVED', 160013, 'Журнал: Энергия не восстановлена жертвоприношением огнём', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Окончание жертвоприношения огнём не принесло энергии.',
         [V.ENERGY, V.HERO], '+energy#EN'),

        ('ACTION_REGENERATE_ENERGY_SACRIFICE_BLOOD_NO_ENERGY_RECEIVED', 160028, 'Журнал: Энергия не восстановлена жертвоприношением кровью', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Окончание жертвоприношения кровью не принесло энергии.',
         [V.ENERGY, V.HERO], '+energy#EN'),

        ('ACTION_REGENERATE_ENERGY_SACRIFICE_KNIFE_NO_ENERGY_RECEIVED', 160029, 'Журнал: Энергия не восстановлена жертвоприношением ножом', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Окончание жертвоприношения ножом не принесло энергии.',
         [V.ENERGY, V.HERO], '+energy#EN'),

        ('ACTION_REGENERATE_ENERGY_SYMBOLS_STONE_NO_ENERGY_RECEIVED', 160014, 'Журнал: Энергия не восстановлена вырезанием символов на камне', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Окончание вырезание символов на камне не принесло энергии.',
         [V.ENERGY, V.HERO], '+energy#EN'),

        ('ACTION_REGENERATE_ENERGY_SYMBOLS_TREE_NO_ENERGY_RECEIVED', 160030, 'Журнал: Энергия не восстановлена вырезанием символов на дереве', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Окончание вырезание символов на дереве не принесло энергии.',
         [V.ENERGY, V.HERO], '+energy#EN'),

        ('ACTION_REGENERATE_ENERGY_SYMBOLS_GROUND_NO_ENERGY_RECEIVED', 160031, 'Журнал: Энергия не восстановлена вырезанием символов на земле', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Окончание вырезание символов на земле не принесло энергии.',
         [V.ENERGY, V.HERO], '+energy#EN'),

        ('ACTION_REGENERATE_ENERGY_INCENSE_START', 160015, 'Журнал: Начало курения благовоний', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Герой начинает курить благовония',
         [V.HERO], None),

        ('ACTION_REGENERATE_ENERGY_MEDITATION_START', 160016, 'Журнал: Начало медитации', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Герой приступает к медитации',
         [V.HERO], None),

        ('ACTION_REGENERATE_ENERGY_PRAY_START', 160017, 'Журнал: Начало молитвы', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Герой начинает молиться.',
         [V.HERO], None),

        ('ACTION_REGENERATE_ENERGY_SACRIFICE_FIRE_START', 160018, 'Журнал: Начало жертвоприношения огнём', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Герой начинает приносить жертву через сжигание останков монстра.',
         [V.HERO], None),

        ('ACTION_REGENERATE_ENERGY_SACRIFICE_BLOOD_START', 160032, 'Журнал: Начало жертвоприношения кровью', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Герой начинает приносить жертву кровью монстра.',
         [V.HERO], None),

        ('ACTION_REGENERATE_ENERGY_SACRIFICE_KNIFE_START', 160033, 'Журнал: Начало жертвоприношения ножом', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Герой начинает приносить жертву, разделывая останки монстра.',
         [V.HERO], None),

        ('ACTION_REGENERATE_ENERGY_SYMBOLS_STONE_START', 160019, 'Журнал: Начало вырезания символов на камне', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Герой начинает вырезать символы на камне',
         [V.HERO], None),

        ('ACTION_REGENERATE_ENERGY_SYMBOLS_TREE_START', 160034, 'Журнал: Начало вырезания символов на дереве', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Герой начинает вырезать символы на дереве',
         [V.HERO], None),

        ('ACTION_REGENERATE_ENERGY_SYMBOLS_GROUND_START', 160035, 'Журнал: Начало вырезания символов на земле', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         'Герой начинает вырезать символы на земле',
         [V.HERO], None),

       ]
