
import smart_imports

smart_imports.all()


V = lexicon_relations.VARIABLE


KEYS = [('CARDS_HEALHERO', 240008, 'Журнал: Лечение', relations.LEXICON_GROUP.CARDS,
         'Герой излечивает небольшое количество здоровья.',
         [V.DATE, V.TIME, V.HERO, V.HEALTH, V.ENERGY], 'hero#N +health#HP'),

        ('CARDS_LIGHTNING', 240010, 'Журнал: Нанесение урона', relations.LEXICON_GROUP.CARDS,
         'Нанесение урона противнику (монстру).',
         [V.DATE, V.TIME, V.MOB, V.HERO, V.DAMAGE, V.ENERGY], 'mob#N -damage#HP'),

        ('CARDS_MONEY', 240012, 'Журнал: Создание денег', relations.LEXICON_GROUP.CARDS,
         'Герой находит небольшое количество монет',
         [V.DATE, V.TIME, V.COINS, V.HERO, V.ENERGY], 'hero#N +coins#G'),

        ('CARDS_RESURRECT', 240014, 'Журнал: Воскрешение', relations.LEXICON_GROUP.CARDS,
         'Герой моментально воскресает.',
         [V.DATE, V.TIME, V.HERO, V.ENERGY], ''),

        ('CARDS_SHORTTELEPORT', 240015, 'Журнал: Короткий телепорт', relations.LEXICON_GROUP.CARDS,
         'Герой телепортируется на небольшое расстояние.',
         [V.DATE, V.TIME, V.HERO, V.ENERGY], ''),

        ('CARDS_LONGTELEPORT', 240016, 'Журнал: Короткий телепорт (критический эффект)', relations.LEXICON_GROUP.CARDS,
         'Герой телепортируется на большое расстояние.',
         [V.DATE, V.TIME, V.HERO, V.ENERGY], ''),

        ('CARDS_HEAL_COMPANION', 240020, 'Журнал: Лечение спутника', relations.LEXICON_GROUP.CARDS,
         'Спутник героя восстанавливает здоровье.',
         [V.DATE, V.TIME, V.HEALTH, V.HERO, V.COMPANION, V.HEALTH, V.ENERGY], 'companion#N +health#HP'),

        ]
