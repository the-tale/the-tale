# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'ANGEL_ABILITY_ARENA_PVP_1X1', 240000, u'Журнал: Отправка на PvP арену', LEXICON_GROUP.ANGEL_ABILITY,
        u'Герой становится в очередь на PvP арену.',
        [V.HERO]),

        (u'ANGEL_ABILITY_ARENA_PVP_1X1_LEAVE_QUEUE', 240001, u'Журнал: Выход из очереди на PvP арену', LEXICON_GROUP.ANGEL_ABILITY,
        u'Герой выходит из очереди на PvP арену.',
        [V.HERO]),

        (u'ANGEL_ABILITY_BUILDING_REPAIR', 240002, u'Журнал: Вызов ремонтника', LEXICON_GROUP.ANGEL_ABILITY,
        u'Вызов духа-ремонтника для починки здания.',
        [V.HERO]),

        (u'ANGEL_ABILITY_BUILDING_REPAIR_CRIT', 240003, u'Журнал: Вызов ремонтника (критический эффект)', LEXICON_GROUP.ANGEL_ABILITY,
        u'Вызов духа-ремонтника для починки здания. (критический эффект)',
        [V.HERO]),

        (u'ANGEL_ABILITY_DROP_ITEM', 240004, u'Журнал: Выкинуть самый дешёвый предмет из рюкзака', LEXICON_GROUP.ANGEL_ABILITY,
        u'У героя из рюкзака пропадает самый дешёвый предмет.',
        [V.DROPPED_ITEM, V.HERO]),

        (u'ANGEL_ABILITY_DROP_ITEM_CRIT', 240005, u'Журнал: Выкинуть самый дешёвый предмет из рюкзака (критическое срабатывание)', LEXICON_GROUP.ANGEL_ABILITY,
        u'У героя из рюкзака пропадает самый дешёвый предмет, герой получает сумму монет, равную стоимости предмета.',
        [V.DROPPED_ITEM, V.COINS, V.HERO]),

        (u'ANGEL_ABILITY_EXPERIENCE', 240006, u'Журнал: Получение опыта', LEXICON_GROUP.ANGEL_ABILITY,
        u'Получение опыта.',
        [V.HERO, V.EXPERIENCE]),

        (u'ANGEL_ABILITY_EXPERIENCE_CRIT', 240007, u'Журнал: Получение опыта (критический эффект)', LEXICON_GROUP.ANGEL_ABILITY,
        u'Получение бОльшего опыта.',
        [V.HERO, V.EXPERIENCE]),

        (u'ANGEL_ABILITY_HEALHERO', 240008, u'Журнал: Лечение', LEXICON_GROUP.ANGEL_ABILITY,
        u'Герой излечивает небольшое количество здоровья.',
        [V.HERO, V.HEALTH]),

        (u'ANGEL_ABILITY_HEALHERO_CRIT', 240009, u'Журнал: Лечение (критический эффект)', LEXICON_GROUP.ANGEL_ABILITY,
        u'Герой восстанавливает существенное количество здоровья.',
        [V.HERO, V.HEALTH]),

        (u'ANGEL_ABILITY_LIGHTNING', 240010, u'Журнал: Нанесение урона', LEXICON_GROUP.ANGEL_ABILITY,
        u'Нанесение урона противнику (монстру).',
        [V.MOB, V.HERO]),

        (u'ANGEL_ABILITY_LIGHTNING_CRIT', 240011, u'Журнал: Нанесение урона (критический эффект)', LEXICON_GROUP.ANGEL_ABILITY,
        u'Нанесение большего урона противнику (монстру).',
        [V.MOB, V.HERO]),

        (u'ANGEL_ABILITY_MONEY', 240012, u'Журнал: Создание денег', LEXICON_GROUP.ANGEL_ABILITY,
        u'Герой находит небольшое количество монет',
        [V.COINS, V.HERO]),

        (u'ANGEL_ABILITY_MONEY_CRIT', 240013, u'Журнал: Создание денег (критический эффект)', LEXICON_GROUP.ANGEL_ABILITY,
        u'Герой находит существенное количесто монет.',
        [V.COINS, V.HERO]),

        (u'ANGEL_ABILITY_RESURRECT', 240014, u'Журнал: Воскрешение', LEXICON_GROUP.ANGEL_ABILITY,
        u'Герой моментально воскресает.',
        [V.HERO]),

        (u'ANGEL_ABILITY_SHORTTELEPORT', 240015, u'Журнал: Короткий телепорт', LEXICON_GROUP.ANGEL_ABILITY,
        u'Герой телепортируется на небольшое расстояние.',
        [V.HERO]),

        (u'ANGEL_ABILITY_SHORTTELEPORT_CRIT', 240016, u'Журнал: Короткий телепорт (критический эффект)', LEXICON_GROUP.ANGEL_ABILITY,
        u'Герой телепортируется на большое расстояние.',
        [V.HERO]),

        (u'ANGEL_ABILITY_STIMULATE', 240017, u'Журнал: Начало задания.', LEXICON_GROUP.ANGEL_ABILITY,
        u'Герой моментально получает задание.',
        [V.HERO]),

        (u'ANGEL_ABILITY_STOCK_UP_ENERGY', 240018, u'Журнал: Запасение энергии', LEXICON_GROUP.ANGEL_ABILITY,
        u'Игрок запасает заряд энергии.',
        [V.ENERGY, V.HERO]),

        (u'ANGEL_ABILITY_STOCK_UP_ENERGY_CRIT', 240019, u'Журнал: Запасение энергии (критический эффект)', LEXICON_GROUP.ANGEL_ABILITY,
        u'Игрок запасает два заряда энергии.',
        [V.ENERGY, V.HERO]),

        ]
