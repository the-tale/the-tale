# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [('ACTION_EQUIPPING_DESCRIPTION', 20000, 'Описание', LEXICON_GROUP.ACTION_EQUIPPING,
        'Краткая декларация того, что делает герой.',
        [V.DATE, V.HERO], None),

        ('ACTION_EQUIPPING_DIARY_CHANGE_EQUAL_ITEMS', 20001, 'Дневник: Обновить предмет', LEXICON_GROUP.ACTION_EQUIPPING,
        'Замена экипированного предмета на предмет с аналогичным названием.',
        [V.DATE, V.ITEM, V.HERO], None),

        ('ACTION_EQUIPPING_DIARY_CHANGE_ITEM', 20002, 'Дневник: Сменить предмет', LEXICON_GROUP.ACTION_EQUIPPING,
        'Замена экипированного предмета на предмет с отличающимся названием',
        [V.DATE, V.UNEQUIPPED, V.HERO, V.EQUIPPED], None),

        ('ACTION_EQUIPPING_DIARY_EQUIP_ITEM', 20003, 'Дневник: Экипировать предмет', LEXICON_GROUP.ACTION_EQUIPPING,
        'Экипировка предмета в первый раз (до этого слот экипировки для предмета был свободен)',
        [V.DATE, V.HERO, V.EQUIPPED], None),

        ]
