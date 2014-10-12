# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'ACTION_EVENT_HABIT_IN_PLACE_AGGRESSIVE_ARTIFACT', 40000, u'Дневник: В городе, черты, агрессивность (артефакт)', LEXICON_GROUP.ACTION_EVENT,
        u'События при посещении города агрессивным героем (артефакт)',
        [V.HERO, V.PLACE, V.ARTIFACT]),

        (u'ACTION_EVENT_HABIT_IN_PLACE_AGGRESSIVE_EXPERIENCE', 40001, u'Дневник: В городе, черты, агрессивность (опыт)', LEXICON_GROUP.ACTION_EVENT,
        u'События при посещении города агрессивным героем (опыт)',
        [V.HERO, V.PLACE, V.EXPERIENCE]),

        (u'ACTION_EVENT_HABIT_IN_PLACE_AGGRESSIVE_MONEY', 40002, u'Дневник: В городе, черты, агрессивность (деньги)', LEXICON_GROUP.ACTION_EVENT,
        u'События при посещении города агрессивным героем (опыт)',
        [V.HERO, V.COINS, V.PLACE]),

        (u'ACTION_EVENT_HABIT_IN_PLACE_AGGRESSIVE_NOTHING', 40003, u'Дневник: В городе, черты, агрессивность (без бонуса)', LEXICON_GROUP.ACTION_EVENT,
        u'События при посещении города агрессивным героем (без бонуса)',
        [V.HERO, V.PLACE]),

        (u'ACTION_EVENT_HABIT_IN_PLACE_DISHONORABLE_ARTIFACT', 40004, u'Дневник: В городе, черты, бесчестие (артефакт)', LEXICON_GROUP.ACTION_EVENT,
        u'События при посещении города бесчестным героем (артефакт)',
        [V.HERO, V.PLACE, V.ARTIFACT]),

        (u'ACTION_EVENT_HABIT_IN_PLACE_DISHONORABLE_EXPERIENCE', 40005, u'Дневник: В городе, черты, бесчестие (опыт)', LEXICON_GROUP.ACTION_EVENT,
        u'События при посещении города бесчестным героем (опыт)',
        [V.HERO, V.PLACE, V.EXPERIENCE]),

        (u'ACTION_EVENT_HABIT_IN_PLACE_DISHONORABLE_MONEY', 40006, u'Дневник: В городе, черты, бесчестие (деньги)', LEXICON_GROUP.ACTION_EVENT,
        u'События при посещении города бесчестным героем (деньги)',
        [V.HERO, V.COINS, V.PLACE]),

        (u'ACTION_EVENT_HABIT_IN_PLACE_DISHONORABLE_NOTHING', 40007, u'Дневник: В городе, черты, бесчестие (без бонуса)', LEXICON_GROUP.ACTION_EVENT,
        u'События при посещении города бесчестным героем (без бонуса)',
        [V.HERO, V.PLACE]),

        (u'ACTION_EVENT_HABIT_IN_PLACE_NOBLE_ARTIFACT', 40008, u'Дневник: В городе, черты, благородство (артефакт)', LEXICON_GROUP.ACTION_EVENT,
        u'События при посещении города благородным героем (артефакт)',
        [V.HERO, V.PLACE, V.ARTIFACT]),

        (u'ACTION_EVENT_HABIT_IN_PLACE_NOBLE_EXPERIENCE', 40009, u'Дневник: В городе, черты, благородство (опыт)', LEXICON_GROUP.ACTION_EVENT,
        u'События при посещении города благородным героем (опыт)',
        [V.HERO, V.PLACE, V.EXPERIENCE]),

        (u'ACTION_EVENT_HABIT_IN_PLACE_NOBLE_MONEY', 40010, u'Дневник: В городе, черты, благородство (деньги)', LEXICON_GROUP.ACTION_EVENT,
        u'События при посещении города благородным героем (деньги)',
        [V.HERO, V.COINS, V.PLACE]),

        (u'ACTION_EVENT_HABIT_IN_PLACE_NOBLE_NOTHING', 40011, u'Дневник: В городе, черты, благородство (без бонуса)', LEXICON_GROUP.ACTION_EVENT,
        u'События при посещении города благородным героем (без бонуса)',
        [V.HERO, V.PLACE]),

        (u'ACTION_EVENT_HABIT_IN_PLACE_PEACEABLE_ARTIFACT', 40012, u'Дневник: В городе, черты, миролюбие (артефакт)', LEXICON_GROUP.ACTION_EVENT,
        u'События при посещении города миролюбивым героем (артефакт)',
        [V.HERO, V.PLACE, V.ARTIFACT]),

        (u'ACTION_EVENT_HABIT_IN_PLACE_PEACEABLE_EXPERIENCE', 40013, u'Дневник: В городе, черты, миролюбие (опыт)', LEXICON_GROUP.ACTION_EVENT,
        u'События при посещении города миролюбивым героем (опыт)',
        [V.HERO, V.PLACE, V.EXPERIENCE]),

        (u'ACTION_EVENT_HABIT_IN_PLACE_PEACEABLE_MONEY', 40014, u'Дневник: В городе, черты, миролюбие (деньги)', LEXICON_GROUP.ACTION_EVENT,
        u'События при посещении города миролюбивым героем (деньги)',
        [V.HERO, V.COINS, V.PLACE]),

        (u'ACTION_EVENT_HABIT_IN_PLACE_PEACEABLE_NOTHING', 40015, u'Дневник: В городе, черты, миролюбие (без бонуса)', LEXICON_GROUP.ACTION_EVENT,
        u'События при посещении города миролюбивым героем (без бонуса)',
        [V.HERO, V.PLACE]),

        (u'ACTION_EVENT_HABIT_MOVE_TO_AGGRESSIVE_ARTIFACT', 40016, u'Дневник: В движении, черты, агрессивность (артефакт)', LEXICON_GROUP.ACTION_EVENT,
        u'События при путешествии агрессивного героя (артефакт)',
        [V.HERO, V.ARTIFACT]),

        (u'ACTION_EVENT_HABIT_MOVE_TO_AGGRESSIVE_EXPERIENCE', 40017, u'Дневник: В движении, черты, агрессивность (опыт)', LEXICON_GROUP.ACTION_EVENT,
        u'События при путешествии агрессивного героя (опыт)',
        [V.HERO, V.EXPERIENCE]),

        (u'ACTION_EVENT_HABIT_MOVE_TO_AGGRESSIVE_MONEY', 40018, u'Дневник: В движении, черты, агрессивность (деньги)', LEXICON_GROUP.ACTION_EVENT,
        u'События при путешествии агрессивного героя (деньги)',
        [V.COINS, V.HERO]),

        (u'ACTION_EVENT_HABIT_MOVE_TO_AGGRESSIVE_NOTHING', 40019, u'Дневник: В движении, черты, агрессивность (без бонуса)', LEXICON_GROUP.ACTION_EVENT,
        u'События при путешествии агрессивного героя (без бонуса)',
        [V.HERO]),

        (u'ACTION_EVENT_HABIT_MOVE_TO_DISHONORABLE_ARTIFACT', 40020, u'Дневник: В движении, черты, бесчестие (артефакт)', LEXICON_GROUP.ACTION_EVENT,
        u'События при путешествии бесчестного героя (артефакт)',
        [V.HERO, V.ARTIFACT]),

        (u'ACTION_EVENT_HABIT_MOVE_TO_DISHONORABLE_EXPERIENCE', 40021, u'Дневник: В движении, черты, бесчестие (опыт)', LEXICON_GROUP.ACTION_EVENT,
        u'События при путешествии бесчестного героя (опыт)',
        [V.HERO, V.EXPERIENCE]),

        (u'ACTION_EVENT_HABIT_MOVE_TO_DISHONORABLE_MONEY', 40022, u'Дневник: В движении, черты, бесчестие (деньги)', LEXICON_GROUP.ACTION_EVENT,
        u'События при путешествии бесчестного героя (деньги)',
        [V.COINS, V.HERO]),

        (u'ACTION_EVENT_HABIT_MOVE_TO_DISHONORABLE_NOTHING', 40023, u'Дневник: В движении, черты, бесчестие (без бонуса)', LEXICON_GROUP.ACTION_EVENT,
        u'События при путешествии бесчестного героя (без бонуса)',
        [V.HERO]),

        (u'ACTION_EVENT_HABIT_MOVE_TO_NOBLE_ARTIFACT', 40024, u'Дневник: В движении, черты, благородство (артефакт)', LEXICON_GROUP.ACTION_EVENT,
        u'События при путешествии благородного героя (артефакт)',
        [V.HERO, V.ARTIFACT]),

        (u'ACTION_EVENT_HABIT_MOVE_TO_NOBLE_EXPERIENCE', 40025, u'Дневник: В движении, черты, благородство (опыт)', LEXICON_GROUP.ACTION_EVENT,
        u'События при путешествии благородного героя (опыт)',
        [V.HERO, V.EXPERIENCE]),

        (u'ACTION_EVENT_HABIT_MOVE_TO_NOBLE_MONEY', 40026, u'Дневник: В движении, черты, благородство (деньги)', LEXICON_GROUP.ACTION_EVENT,
        u'События при путешествии благородного героя (деньги)',
        [V.COINS, V.HERO]),

        (u'ACTION_EVENT_HABIT_MOVE_TO_NOBLE_NOTHING', 40027, u'Дневник: В движении, черты, благородство (без бонуса)', LEXICON_GROUP.ACTION_EVENT,
        u'События при путешествии благородного героя (без бонуса)',
        [V.HERO]),

        (u'ACTION_EVENT_HABIT_MOVE_TO_PEACEABLE_ARTIFACT', 40028, u'Дневник: В движении, черты, миролюбие (артефакт)', LEXICON_GROUP.ACTION_EVENT,
        u'События при путешествии миролюбивого героя (артефакт)',
        [V.HERO, V.ARTIFACT]),

        (u'ACTION_EVENT_HABIT_MOVE_TO_PEACEABLE_EXPERIENCE', 40029, u'Дневник: В движении, черты, миролюбие (опыт)', LEXICON_GROUP.ACTION_EVENT,
        u'События при путешествии миролюбивого героя (опыт)',
        [V.HERO, V.EXPERIENCE]),

        (u'ACTION_EVENT_HABIT_MOVE_TO_PEACEABLE_MONEY', 40030, u'Дневник: В движении, черты, миролюбие (деньги)', LEXICON_GROUP.ACTION_EVENT,
        u'События при путешествии миролюбивого героя (деньги)',
        [V.COINS, V.HERO]),

        (u'ACTION_EVENT_HABIT_MOVE_TO_PEACEABLE_NOTHING', 40031, u'Дневник: В движении, черты, миролюбие (без бонуса)', LEXICON_GROUP.ACTION_EVENT,
        u'События при путешествии миролюбивого героя (без бонуса)',
        [V.HERO]),

        ]
