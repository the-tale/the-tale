# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [('ACTION_TRADING_DESCRIPTION', 220000, 'Описание', LEXICON_GROUP.ACTION_TRADING,
        'Краткая декларация того, что делает герой.',
        [V.HERO], None),

        ('ACTION_TRADING_SELL_ITEM', 220001, 'Журнал: Продажа', LEXICON_GROUP.ACTION_TRADING,
        'Герой продаёт предмет.',
        [V.COINS, V.HERO, V.ARTIFACT], 'hero#N +coins#G'),

        ('ACTION_TRADING_START', 220002, 'Журнал: Начало', LEXICON_GROUP.ACTION_TRADING,
        'Герой начинает торговлю.',
        [V.HERO], None),

        ]
