
import smart_imports

smart_imports.all()


V = lexicon_relations.VARIABLE


KEYS = [('ANGEL_ABILITY_HEALHERO', 240008, 'Журнал: Лечение', relations.LEXICON_GROUP.ANGEL_ABILITY,
         'Герой излечивает небольшое количество здоровья.',
         [V.DATE, V.TIME, V.HERO, V.HEALTH, V.ENERGY], 'hero#N +health#HP -energy#EN'),

        ('ANGEL_ABILITY_HEALHERO_CRIT', 240009, 'Журнал: Лечение (критический эффект)', relations.LEXICON_GROUP.ANGEL_ABILITY,
         'Герой восстанавливает существенное количество здоровья.',
         [V.DATE, V.TIME, V.HERO, V.HEALTH, V.ENERGY], 'hero#N +health#HP -energy#EN'),

        ('ANGEL_ABILITY_LIGHTNING', 240010, 'Журнал: Нанесение урона', relations.LEXICON_GROUP.ANGEL_ABILITY,
         'Нанесение урона противнику (монстру).',
         [V.DATE, V.TIME, V.MOB, V.HERO, V.DAMAGE, V.ENERGY], 'mob#N -damage#HP -energy#EN'),

        ('ANGEL_ABILITY_LIGHTNING_CRIT', 240011, 'Журнал: Нанесение урона (критический эффект)', relations.LEXICON_GROUP.ANGEL_ABILITY,
         'Нанесение большего урона противнику (монстру).',
         [V.DATE, V.TIME, V.MOB, V.HERO, V.DAMAGE, V.ENERGY], 'mob#N -damage#HP -energy#EN'),

        ('ANGEL_ABILITY_MONEY', 240012, 'Журнал: Создание денег', relations.LEXICON_GROUP.ANGEL_ABILITY,
         'Герой находит небольшое количество монет',
         [V.DATE, V.TIME, V.COINS, V.HERO, V.ENERGY], 'hero#N +coins#G -energy#EN'),

        ('ANGEL_ABILITY_MONEY_CRIT', 240013, 'Журнал: Создание денег (критический эффект)', relations.LEXICON_GROUP.ANGEL_ABILITY,
         'Герой находит существенное количество монет.',
         [V.DATE, V.TIME, V.COINS, V.HERO, V.ENERGY], 'hero#N +coins#G -energy#EN'),

        ('ANGEL_ABILITY_RESURRECT', 240014, 'Журнал: Воскрешение', relations.LEXICON_GROUP.ANGEL_ABILITY,
         'Герой моментально воскресает.',
         [V.DATE, V.TIME, V.HERO, V.ENERGY], '-energy#EN'),

        ('ANGEL_ABILITY_SHORTTELEPORT', 240015, 'Журнал: Короткий телепорт', relations.LEXICON_GROUP.ANGEL_ABILITY,
         'Герой телепортируется на небольшое расстояние.',
         [V.DATE, V.TIME, V.HERO, V.ENERGY], '-energy#EN'),

        ('ANGEL_ABILITY_SHORTTELEPORT_CRIT', 240016, 'Журнал: Короткий телепорт (критический эффект)', relations.LEXICON_GROUP.ANGEL_ABILITY,
         'Герой телепортируется на большое расстояние.',
         [V.DATE, V.TIME, V.HERO, V.ENERGY], '-energy#EN'),

        ('ANGEL_ABILITY_HEAL_COMPANION', 240020, 'Журнал: Лечение спутника', relations.LEXICON_GROUP.ANGEL_ABILITY,
         'Спутник героя восстанавливает здоровье.',
         [V.DATE, V.TIME, V.HEALTH, V.HERO, V.COMPANION, V.HEALTH, V.ENERGY], 'companion#N +health#HP -energy#EN'),

        ('ANGEL_ABILITY_HEAL_COMPANION_CRIT', 240021, 'Журнал: Лечение спутника (критический эффект)', relations.LEXICON_GROUP.ANGEL_ABILITY,
         'Спутник героя восстанавливает больше здоровья.',
         [V.DATE, V.TIME, V.HEALTH, V.HERO, V.COMPANION, V.HEALTH, V.ENERGY], 'companion#N +health#HP -energy#EN'),

        ]
