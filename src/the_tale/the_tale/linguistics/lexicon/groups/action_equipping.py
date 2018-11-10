
import smart_imports

smart_imports.all()


V = lexicon_relations.VARIABLE


KEYS = [('ACTION_EQUIPPING_DESCRIPTION', 20000, 'Описание', relations.LEXICON_GROUP.ACTION_EQUIPPING,
         'Краткая декларация того, что делает герой.',
         [V.DATE, V.TIME, V.HERO], None),

        ('ACTION_EQUIPPING_DIARY_CHANGE_EQUAL_ITEMS', 20001, 'Дневник: Обновить предмет', relations.LEXICON_GROUP.ACTION_EQUIPPING,
         'Замена экипированного предмета на предмет с аналогичным названием.',
         [V.DATE, V.TIME, V.ITEM, V.HERO], None),

        ('ACTION_EQUIPPING_DIARY_CHANGE_ITEM', 20002, 'Дневник: Сменить предмет', relations.LEXICON_GROUP.ACTION_EQUIPPING,
         'Замена экипированного предмета на предмет с отличающимся названием',
         [V.DATE, V.TIME, V.UNEQUIPPED, V.HERO, V.EQUIPPED], None),

        ('ACTION_EQUIPPING_DIARY_EQUIP_ITEM', 20003, 'Дневник: Экипировать предмет', relations.LEXICON_GROUP.ACTION_EQUIPPING,
         'Экипировка предмета в первый раз (до этого слот экипировки для предмета был свободен)',
         [V.DATE, V.TIME, V.HERO, V.EQUIPPED], None),

        ]
