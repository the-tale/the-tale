
import smart_imports

smart_imports.all()


V = lexicon_relations.VARIABLE


KEYS = [('HERO_COMMON_JOURNAL_LEVEL_UP', 300005, 'Журнал: Получение уровня', relations.LEXICON_GROUP.HERO_COMMON,
         'Герой получает уровень.',
         [V.DATE, V.TIME, V.HERO, V.LEVEL], None),

        ('HERO_COMMON_JOURNAL_RETURN_CHILD_GIFT', 300006, 'Журнал: Детский подарок вернулся к ребёнку', relations.LEXICON_GROUP.HERO_COMMON,
         'Найденный детский подарок пропадает из рюкзака и возвращается к ребёнку.',
         [V.DATE, V.TIME, V.HERO, V.ARTIFACT], None),
        ]
