# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'ACTION_REGENERATE_ENERGY_INCENSE_DESCRIPTION', 160000, u'Описание: курение благовоний', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Краткая декларация того, что делает герой.',
         [V.HERO], None),

        (u'ACTION_REGENERATE_ENERGY_MEDITATION_DESCRIPTION', 160001, u'Описание: медитация', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Краткая декларация того, что делает герой.',
         [V.HERO], None),

        (u'ACTION_REGENERATE_ENERGY_PRAY_DESCRIPTION', 160002, u'Описание: молитва', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Краткая декларация того, что делает герой.',
         [V.HERO], None),

        (u'ACTION_REGENERATE_ENERGY_SACRIFICE_FIRE_DESCRIPTION', 160003, u'Описание: жертвоприношение огнём', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Краткая декларация того, что герой приносит жертву, сжигая останки противника на огне.',
         [V.HERO], None),

        (u'ACTION_REGENERATE_ENERGY_SACRIFICE_BLOOD_DESCRIPTION', 160020, u'Описание: жертвоприношение кровью', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Краткая декларация того, что герой приносит жертву через ритуал с кровью.',
         [V.HERO], None),

        (u'ACTION_REGENERATE_ENERGY_SACRIFICE_KNIFE_DESCRIPTION', 160021, u'Описание: жертвоприношение ножом', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Краткая декларация того, что герой приносит жертву, разделывая её на мелкие кусочки.',
         [V.HERO], None),

        (u'ACTION_REGENERATE_ENERGY_SYMBOLS_STONE_DESCRIPTION', 160004, u'Описание: вырезание символов на камне', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Краткая декларация того, что герой вырезает волшебные руны на камне.',
         [V.HERO], None),

        (u'ACTION_REGENERATE_ENERGY_SYMBOLS_TREE_DESCRIPTION', 160022, u'Описание: вырезание символов на дереве', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Краткая декларация того, что герой вырезает волшебные руны на дереве.',
         [V.HERO], None),

        (u'ACTION_REGENERATE_ENERGY_SYMBOLS_GROUND_DESCRIPTION', 160023, u'Описание: вырезание символов на земле', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Краткая декларация того, что герой пишет волшебные руны на земле.',
         [V.HERO], None),

        (u'ACTION_REGENERATE_ENERGY_INCENSE_ENERGY_RECEIVED', 160005, u'Журнал: Получение энергии курением благовоний', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Окончание курения благовоний и восстановление части энергии',
         [V.ENERGY, V.HERO], u'+energy#EN'),

        (u'ACTION_REGENERATE_ENERGY_MEDITATION_ENERGY_RECEIVED', 160006, u'Журнал: Получение энергии медитацией', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Окончание медитации и восстановление части энергии',
         [V.ENERGY, V.HERO], u'+energy#EN'),

        (u'ACTION_REGENERATE_ENERGY_PRAY_ENERGY_RECEIVED', 160007, u'Журнал: Получение энергии молитвой', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Окончание молитвы и восстановление части энергии.',
         [V.ENERGY, V.HERO], u'+energy#EN'),

        (u'ACTION_REGENERATE_ENERGY_SACRIFICE_FIRE_ENERGY_RECEIVED', 160008, u'Журнал: Получение энергии жертвоприношением огнём', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Окончание жертвоприношения с использованием огня и восстановление части энергии',
         [V.ENERGY, V.HERO], u'+energy#EN'),

        (u'ACTION_REGENERATE_ENERGY_SACRIFICE_BLOOD_ENERGY_RECEIVED', 160024, u'Журнал: Получение энергии жертвоприношением кровью', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Окончание жертвоприношения с использованием крови и восстановление части энергии',
         [V.ENERGY, V.HERO], u'+energy#EN'),

        (u'ACTION_REGENERATE_ENERGY_SACRIFICE_KNIFE_ENERGY_RECEIVED', 160025, u'Журнал: Получение энергии жертвоприношением ножом', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Окончание жертвоприношения с использованием ножа и восстановление части энергии',
         [V.ENERGY, V.HERO], u'+energy#EN'),

        (u'ACTION_REGENERATE_ENERGY_SYMBOLS_STONE_ENERGY_RECEIVED', 160009, u'Журнал: Получение энергии вырезанием символов на камне', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Окончание вырезания символов на камне и восстановление части энергии',
        [V.ENERGY, V.HERO], u'+energy#EN'),

        (u'ACTION_REGENERATE_ENERGY_SYMBOLS_TREE_ENERGY_RECEIVED', 160026, u'Журнал: Получение энергии вырезанием символов на дереве', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Окончание вырезания символов на дереве и восстановление части энергии',
         [V.ENERGY, V.HERO], u'+energy#EN'),

        (u'ACTION_REGENERATE_ENERGY_SYMBOLS_GROUND_ENERGY_RECEIVED', 160027, u'Журнал: Получение энергии вырезанием символов на земле', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Окончание вырезания символов на земле и восстановление части энергии',
         [V.ENERGY, V.HERO], u'+energy#EN'),

        (u'ACTION_REGENERATE_ENERGY_INCENSE_NO_ENERGY_RECEIVED', 160010, u'Журнал: Энергия не восстановлена курением благовоний', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Окончание курения благовоний.',
         [V.ENERGY, V.HERO], u'+energy#EN'),

        (u'ACTION_REGENERATE_ENERGY_MEDITATION_NO_ENERGY_RECEIVED', 160011, u'Журнал: Энергия не восстановлена медитацией', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Окончание медитации.',
         [V.ENERGY, V.HERO], u'+energy#EN'),

        (u'ACTION_REGENERATE_ENERGY_PRAY_NO_ENERGY_RECEIVED', 160012, u'Журнал: Энергия не восстановлена молитвой', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Окончание молитвы.',
         [V.ENERGY, V.HERO], u'+energy#EN'),

        (u'ACTION_REGENERATE_ENERGY_SACRIFICE_FIRE_NO_ENERGY_RECEIVED', 160013, u'Журнал: Энергия не восстановлена жертвоприношением огнём', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Окончание жертвоприношения огнём не принесло энергии.',
         [V.ENERGY, V.HERO], u'+energy#EN'),

        (u'ACTION_REGENERATE_ENERGY_SACRIFICE_BLOOD_NO_ENERGY_RECEIVED', 160028, u'Журнал: Энергия не восстановлена жертвоприношением кровью', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Окончание жертвоприношения кровью не принесло энергии.',
         [V.ENERGY, V.HERO], u'+energy#EN'),

        (u'ACTION_REGENERATE_ENERGY_SACRIFICE_KNIFE_NO_ENERGY_RECEIVED', 160029, u'Журнал: Энергия не восстановлена жертвоприношением ножом', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Окончание жертвоприношения ножом не принесло энергии.',
         [V.ENERGY, V.HERO], u'+energy#EN'),

        (u'ACTION_REGENERATE_ENERGY_SYMBOLS_STONE_NO_ENERGY_RECEIVED', 160014, u'Журнал: Энергия не восстановлена вырезанием символов на камне', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Окончание вырезание символов на камне не принесло энергии.',
         [V.ENERGY, V.HERO], u'+energy#EN'),

        (u'ACTION_REGENERATE_ENERGY_SYMBOLS_TREE_NO_ENERGY_RECEIVED', 160030, u'Журнал: Энергия не восстановлена вырезанием символов на дереве', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Окончание вырезание символов на дереве не принесло энергии.',
         [V.ENERGY, V.HERO], u'+energy#EN'),

        (u'ACTION_REGENERATE_ENERGY_SYMBOLS_GROUND_NO_ENERGY_RECEIVED', 160031, u'Журнал: Энергия не восстановлена вырезанием символов на земле', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Окончание вырезание символов на земле не принесло энергии.',
         [V.ENERGY, V.HERO], u'+energy#EN'),

        (u'ACTION_REGENERATE_ENERGY_INCENSE_START', 160015, u'Журнал: Начало курения благовоний', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Герой начинает курить благовония',
         [V.HERO], None),

        (u'ACTION_REGENERATE_ENERGY_MEDITATION_START', 160016, u'Журнал: Начало медитации', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Герой приступает к медитации',
         [V.HERO], None),

        (u'ACTION_REGENERATE_ENERGY_PRAY_START', 160017, u'Журнал: Начало молитвы', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Герой начинает молиться.',
         [V.HERO], None),

        (u'ACTION_REGENERATE_ENERGY_SACRIFICE_FIRE_START', 160018, u'Журнал: Начало жертвоприношения огнём', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Герой начинает приносить жертву через сжигание останков монстра.',
         [V.HERO], None),

        (u'ACTION_REGENERATE_ENERGY_SACRIFICE_BLOOD_START', 160032, u'Журнал: Начало жертвоприношения кровью', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Герой начинает приносить жертву кровью монстра.',
         [V.HERO], None),

        (u'ACTION_REGENERATE_ENERGY_SACRIFICE_KNIFE_START', 160033, u'Журнал: Начало жертвоприношения ножом', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Герой начинает приносить жертву, разделывая останки монстра.',
         [V.HERO], None),

        (u'ACTION_REGENERATE_ENERGY_SYMBOLS_STONE_START', 160019, u'Журнал: Начало вырезания символов на камне', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Герой начинает вырезать символы на камне',
         [V.HERO], None),

        (u'ACTION_REGENERATE_ENERGY_SYMBOLS_TREE_START', 160034, u'Журнал: Начало вырезания символов на дереве', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Герой начинает вырезать символы на дереве',
         [V.HERO], None),

        (u'ACTION_REGENERATE_ENERGY_SYMBOLS_GROUND_START', 160035, u'Журнал: Начало вырезания символов на земле', LEXICON_GROUP.ACTION_REGENERATE_ENERGY,
         u'Герой начинает вырезать символы на земле',
         [V.HERO], None),

       ]
