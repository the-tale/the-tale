
import smart_imports

smart_imports.all()


V = lexicon_relations.VARIABLE


KEYS = [('ACTION_TRADING_DESCRIPTION', 220000, 'Описание', relations.LEXICON_GROUP.ACTION_TRADING,
         'Краткая декларация того, что делает герой.',
         [V.DATE, V.TIME, V.HERO], None),

        ('ACTION_TRADING_SELL_ITEM', 220001, 'Журнал: Продажа', relations.LEXICON_GROUP.ACTION_TRADING,
         'Герой продаёт предмет.',
         [V.DATE, V.TIME, V.COINS, V.HERO, V.ARTIFACT], 'hero#N +coins#G'),

        ('ACTION_TRADING_START', 220002, 'Журнал: Начало', relations.LEXICON_GROUP.ACTION_TRADING,
         'Герой начинает торговлю.',
         [V.DATE, V.TIME, V.HERO], None),

        ]
