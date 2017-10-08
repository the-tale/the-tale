
from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [('ANGEL_ABILITY_ARENA_PVP_1X1', 240000, 'Журнал: Отправка на PvP арену', LEXICON_GROUP.ANGEL_ABILITY,
        'Герой становится в очередь на PvP арену.',
        [V.DATE, V.TIME, V.HERO], None),

        ('ANGEL_ABILITY_ARENA_PVP_1X1_LEAVE_QUEUE', 240001, 'Журнал: Выход из очереди на PvP арену', LEXICON_GROUP.ANGEL_ABILITY,
        'Герой выходит из очереди на PvP арену.',
        [V.DATE, V.TIME, V.HERO], None),

        ('ANGEL_ABILITY_DROP_ITEM', 240004, 'Журнал: Выкинуть самый дешёвый предмет из рюкзака', LEXICON_GROUP.ANGEL_ABILITY,
        'У героя из рюкзака пропадает самый дешёвый предмет.',
        [V.DATE, V.TIME, V.DROPPED_ITEM, V.HERO], None),

        ('ANGEL_ABILITY_DROP_ITEM_CRIT', 240005, 'Журнал: Выкинуть самый дешёвый предмет из рюкзака (критическое срабатывание)', LEXICON_GROUP.ANGEL_ABILITY,
        'У героя из рюкзака пропадает самый дешёвый предмет, герой получает сумму монет, равную стоимости предмета.',
        [V.DATE, V.TIME, V.DROPPED_ITEM, V.COINS, V.HERO], 'hero#N +coins#G'),

        ('ANGEL_ABILITY_EXPERIENCE', 240006, 'Журнал: Получение опыта', LEXICON_GROUP.ANGEL_ABILITY,
        'Получение опыта.',
        [V.DATE, V.TIME, V.HERO, V.EXPERIENCE], 'hero#N +experience#EXP'),

        ('ANGEL_ABILITY_EXPERIENCE_CRIT', 240007, 'Журнал: Получение опыта (критический эффект)', LEXICON_GROUP.ANGEL_ABILITY,
        'Получение большего опыта.',
        [V.DATE, V.TIME, V.HERO, V.EXPERIENCE], 'hero#N +experience#EXP'),

        ('ANGEL_ABILITY_HEALHERO', 240008, 'Журнал: Лечение', LEXICON_GROUP.ANGEL_ABILITY,
        'Герой излечивает небольшое количество здоровья.',
        [V.DATE, V.TIME, V.HERO, V.HEALTH], 'hero#N +health#HP'),

        ('ANGEL_ABILITY_HEALHERO_CRIT', 240009, 'Журнал: Лечение (критический эффект)', LEXICON_GROUP.ANGEL_ABILITY,
        'Герой восстанавливает существенное количество здоровья.',
        [V.DATE, V.TIME, V.HERO, V.HEALTH], 'hero#N +health#HP'),

        ('ANGEL_ABILITY_LIGHTNING', 240010, 'Журнал: Нанесение урона', LEXICON_GROUP.ANGEL_ABILITY,
        'Нанесение урона противнику (монстру).',
        [V.DATE, V.TIME, V.MOB, V.HERO, V.DAMAGE], 'mob#N -damage#HP'),

        ('ANGEL_ABILITY_LIGHTNING_CRIT', 240011, 'Журнал: Нанесение урона (критический эффект)', LEXICON_GROUP.ANGEL_ABILITY,
        'Нанесение большего урона противнику (монстру).',
        [V.DATE, V.TIME, V.MOB, V.HERO, V.DAMAGE], 'mob#N -damage#HP'),

        ('ANGEL_ABILITY_MONEY', 240012, 'Журнал: Создание денег', LEXICON_GROUP.ANGEL_ABILITY,
        'Герой находит небольшое количество монет',
        [V.DATE, V.TIME, V.COINS, V.HERO], 'hero#N +coins#G'),

        ('ANGEL_ABILITY_MONEY_CRIT', 240013, 'Журнал: Создание денег (критический эффект)', LEXICON_GROUP.ANGEL_ABILITY,
        'Герой находит существенное количество монет.',
        [V.DATE, V.TIME, V.COINS, V.HERO], 'hero#N +coins#G'),

        ('ANGEL_ABILITY_RESURRECT', 240014, 'Журнал: Воскрешение', LEXICON_GROUP.ANGEL_ABILITY,
        'Герой моментально воскресает.',
        [V.DATE, V.TIME, V.HERO], None),

        ('ANGEL_ABILITY_SHORTTELEPORT', 240015, 'Журнал: Короткий телепорт', LEXICON_GROUP.ANGEL_ABILITY,
        'Герой телепортируется на небольшое расстояние.',
        [V.DATE, V.TIME, V.HERO], None),

        ('ANGEL_ABILITY_SHORTTELEPORT_CRIT', 240016, 'Журнал: Короткий телепорт (критический эффект)', LEXICON_GROUP.ANGEL_ABILITY,
        'Герой телепортируется на большое расстояние.',
        [V.DATE, V.TIME, V.HERO], None),

        ('ANGEL_ABILITY_STIMULATE', 240017, 'Журнал: Начало задания.', LEXICON_GROUP.ANGEL_ABILITY,
        'Герой моментально получает задание.',
        [V.DATE, V.TIME, V.HERO], None),

        ('ANGEL_ABILITY_STOCK_UP_ENERGY', 240018, 'Журнал: Запасение энергии', LEXICON_GROUP.ANGEL_ABILITY,
        'Игрок запасает бонусную энергию.',
        [V.DATE, V.TIME, V.ENERGY, V.HERO], 'hero#N +energy#EN'),

        ('ANGEL_ABILITY_STOCK_UP_ENERGY_CRIT', 240019, 'Журнал: Запасение энергии (критический эффект)', LEXICON_GROUP.ANGEL_ABILITY,
        'Игрок запасает два заряда энергии.',
        [V.DATE, V.TIME, V.ENERGY, V.HERO], 'hero#N +energy#EN'),

        ('ANGEL_ABILITY_HEAL_COMPANION', 240020, 'Журнал: Лечение спутника', LEXICON_GROUP.ANGEL_ABILITY,
        'Спутник героя восстанавливает здоровье.',
        [V.DATE, V.TIME, V.HEALTH, V.HERO, V.COMPANION, V.HEALTH], 'companion#N +health#HP'),

        ('ANGEL_ABILITY_HEAL_COMPANION_CRIT', 240021, 'Журнал: Лечение спутника (критический эффект)', LEXICON_GROUP.ANGEL_ABILITY,
        'Спутник героя восстанавливает больше здоровья.',
        [V.DATE, V.TIME, V.HEALTH, V.HERO, V.COMPANION, V.HEALTH], 'companion#N +health#HP'),

        ]
