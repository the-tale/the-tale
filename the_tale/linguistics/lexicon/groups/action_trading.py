# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'ACTION_TRADING_DESCRIPTION', 220000, u'Описание', LEXICON_GROUP.ACTION_TRADING,
        u'Краткая декларация того, что делает герой.',
        [V.HERO]),

        (u'ACTION_TRADING_SELL_ITEM', 220001, u'Журнал: Продажа', LEXICON_GROUP.ACTION_TRADING,
        u'Герой продаёт предмет.',
        [V.COINS, V.HERO, V.ARTIFACT]),

        (u'ACTION_TRADING_START', 220002, u'Журнал: Начало', LEXICON_GROUP.ACTION_TRADING,
        u'Герой начинает торговлю.',
        [V.HERO]),

        ]
