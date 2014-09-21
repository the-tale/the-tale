# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'ACTION_EQUIPPING_DESCRIPTION', 20000, u'Описание', LEXICON_GROUP.ACTION_EQUIPPING,
        u'Краткая декларация того, что делает герой.',
        [V.HERO]),

        (u'ACTION_EQUIPPING_DIARY_CHANGE_EQUAL_ITEMS', 20001, u'Дневник: Обновить предмет', LEXICON_GROUP.ACTION_EQUIPPING,
        u'Замена экипированного предмета на предмет с аналогичным названием.',
        [V.ITEM, V.HERO]),

        (u'ACTION_EQUIPPING_DIARY_CHANGE_ITEM', 20002, u'Дневник: Сменить предмет', LEXICON_GROUP.ACTION_EQUIPPING,
        u'Замена экипированного предмета на предмет с отличающимся названием',
        [V.UNEQUIPPED, V.HERO, V.EQUIPPED]),

        (u'ACTION_EQUIPPING_DIARY_EQUIP_ITEM', 20003, u'Дневник: Экипировать предмет', LEXICON_GROUP.ACTION_EQUIPPING,
        u'Экипировка предмета в первый раз (до этого слот экипировки для предмета был свободен)',
        [V.HERO, V.EQUIPPED]),

        ]
        