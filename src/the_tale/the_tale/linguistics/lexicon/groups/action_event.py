
import smart_imports

smart_imports.all()


V = lexicon_relations.VARIABLE


KEYS = [('ACTION_EVENT_HABIT_IN_PLACE_AGGRESSIVE_ARTIFACT', 40000, 'Дневник: В городе, черты, агрессивность (артефакт)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при посещении города агрессивным героем (артефакт)',
         [V.DATE, V.TIME, V.HERO, V.PLACE, V.ARTIFACT], None),

        ('ACTION_EVENT_HABIT_IN_PLACE_AGGRESSIVE_EXPERIENCE', 40001, 'Дневник: В городе, черты, агрессивность (опыт)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при посещении города агрессивным героем (опыт)',
         [V.DATE, V.TIME, V.HERO, V.PLACE, V.EXPERIENCE], 'hero#N +experience#EXP'),

        ('ACTION_EVENT_HABIT_IN_PLACE_AGGRESSIVE_MONEY', 40002, 'Дневник: В городе, черты, агрессивность (деньги)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при посещении города агрессивным героем (деньги)',
         [V.DATE, V.TIME, V.HERO, V.COINS, V.PLACE], 'hero#N +coins#G'),

        ('ACTION_EVENT_HABIT_IN_PLACE_AGGRESSIVE_NOTHING', 40003, 'Дневник: В городе, черты, агрессивность (без бонуса)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при посещении города агрессивным героем (без бонуса)',
         [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_EVENT_HABIT_IN_PLACE_DISHONORABLE_ARTIFACT', 40004, 'Дневник: В городе, черты, бесчестие (артефакт)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при посещении города бесчестным героем (артефакт)',
         [V.DATE, V.TIME, V.HERO, V.PLACE, V.ARTIFACT], None),

        ('ACTION_EVENT_HABIT_IN_PLACE_DISHONORABLE_EXPERIENCE', 40005, 'Дневник: В городе, черты, бесчестие (опыт)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при посещении города бесчестным героем (опыт)',
         [V.DATE, V.TIME, V.HERO, V.PLACE, V.EXPERIENCE], 'hero#N +experience#EXP'),

        ('ACTION_EVENT_HABIT_IN_PLACE_DISHONORABLE_MONEY', 40006, 'Дневник: В городе, черты, бесчестие (деньги)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при посещении города бесчестным героем (деньги)',
         [V.DATE, V.TIME, V.HERO, V.COINS, V.PLACE], 'hero#N +coins#G'),

        ('ACTION_EVENT_HABIT_IN_PLACE_DISHONORABLE_NOTHING', 40007, 'Дневник: В городе, черты, бесчестие (без бонуса)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при посещении города бесчестным героем (без бонуса)',
         [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_EVENT_HABIT_IN_PLACE_NOBLE_ARTIFACT', 40008, 'Дневник: В городе, черты, благородство (артефакт)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при посещении города благородным героем (артефакт)',
         [V.DATE, V.TIME, V.HERO, V.PLACE, V.ARTIFACT], None),

        ('ACTION_EVENT_HABIT_IN_PLACE_NOBLE_EXPERIENCE', 40009, 'Дневник: В городе, черты, благородство (опыт)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при посещении города благородным героем (опыт)',
         [V.DATE, V.TIME, V.HERO, V.PLACE, V.EXPERIENCE], 'hero#N +experience#EXP'),

        ('ACTION_EVENT_HABIT_IN_PLACE_NOBLE_MONEY', 40010, 'Дневник: В городе, черты, благородство (деньги)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при посещении города благородным героем (деньги)',
         [V.DATE, V.TIME, V.HERO, V.COINS, V.PLACE], 'hero#N +coins#G'),

        ('ACTION_EVENT_HABIT_IN_PLACE_NOBLE_NOTHING', 40011, 'Дневник: В городе, черты, благородство (без бонуса)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при посещении города благородным героем (без бонуса)',
         [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_EVENT_HABIT_IN_PLACE_PEACEABLE_ARTIFACT', 40012, 'Дневник: В городе, черты, миролюбие (артефакт)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при посещении города миролюбивым героем (артефакт)',
         [V.DATE, V.TIME, V.HERO, V.PLACE, V.ARTIFACT], None),

        ('ACTION_EVENT_HABIT_IN_PLACE_PEACEABLE_EXPERIENCE', 40013, 'Дневник: В городе, черты, миролюбие (опыт)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при посещении города миролюбивым героем (опыт)',
         [V.DATE, V.TIME, V.HERO, V.PLACE, V.EXPERIENCE], 'hero#N +experience#EXP'),

        ('ACTION_EVENT_HABIT_IN_PLACE_PEACEABLE_MONEY', 40014, 'Дневник: В городе, черты, миролюбие (деньги)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при посещении города миролюбивым героем (деньги)',
         [V.DATE, V.TIME, V.HERO, V.COINS, V.PLACE], 'hero#N +coins#G'),

        ('ACTION_EVENT_HABIT_IN_PLACE_PEACEABLE_NOTHING', 40015, 'Дневник: В городе, черты, миролюбие (без бонуса)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при посещении города миролюбивым героем (без бонуса)',
         [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_EVENT_HABIT_MOVE_SIMPLE_AGGRESSIVE_ARTIFACT', 40016, 'Дневник: В движении, черты, агрессивность (артефакт)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при путешествии агрессивного героя (артефакт)',
         [V.DATE, V.TIME, V.HERO, V.ARTIFACT], None),

        ('ACTION_EVENT_HABIT_MOVE_SIMPLE_AGGRESSIVE_EXPERIENCE', 40017, 'Дневник: В движении, черты, агрессивность (опыт)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при путешествии агрессивного героя (опыт)',
         [V.DATE, V.TIME, V.HERO, V.EXPERIENCE], 'hero#N +experience#EXP'),

        ('ACTION_EVENT_HABIT_MOVE_SIMPLE_AGGRESSIVE_MONEY', 40018, 'Дневник: В движении, черты, агрессивность (деньги)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при путешествии агрессивного героя (деньги)',
         [V.DATE, V.TIME, V.COINS, V.HERO], 'hero#N +coins#G'),

        ('ACTION_EVENT_HABIT_MOVE_SIMPLE_AGGRESSIVE_NOTHING', 40019, 'Дневник: В движении, черты, агрессивность (без бонуса)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при путешествии агрессивного героя (без бонуса)',
         [V.DATE, V.TIME, V.HERO], None),

        ('ACTION_EVENT_HABIT_MOVE_SIMPLE_DISHONORABLE_ARTIFACT', 40020, 'Дневник: В движении, черты, бесчестие (артефакт)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при путешествии бесчестного героя (артефакт)',
         [V.DATE, V.TIME, V.HERO, V.ARTIFACT], None),

        ('ACTION_EVENT_HABIT_MOVE_SIMPLE_DISHONORABLE_EXPERIENCE', 40021, 'Дневник: В движении, черты, бесчестие (опыт)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при путешествии бесчестного героя (опыт)',
         [V.DATE, V.TIME, V.HERO, V.EXPERIENCE], 'hero#N +experience#EXP'),

        ('ACTION_EVENT_HABIT_MOVE_SIMPLE_DISHONORABLE_MONEY', 40022, 'Дневник: В движении, черты, бесчестие (деньги)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при путешествии бесчестного героя (деньги)',
         [V.DATE, V.TIME, V.COINS, V.HERO], 'hero#N +coins#G'),

        ('ACTION_EVENT_HABIT_MOVE_SIMPLE_DISHONORABLE_NOTHING', 40023, 'Дневник: В движении, черты, бесчестие (без бонуса)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при путешествии бесчестного героя (без бонуса)',
         [V.DATE, V.TIME, V.HERO], None),

        ('ACTION_EVENT_HABIT_MOVE_SIMPLE_NOBLE_ARTIFACT', 40024, 'Дневник: В движении, черты, благородство (артефакт)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при путешествии благородного героя (артефакт)',
         [V.DATE, V.TIME, V.HERO, V.ARTIFACT], None),

        ('ACTION_EVENT_HABIT_MOVE_SIMPLE_NOBLE_EXPERIENCE', 40025, 'Дневник: В движении, черты, благородство (опыт)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при путешествии благородного героя (опыт)',
         [V.DATE, V.TIME, V.HERO, V.EXPERIENCE], 'hero#N +experience#EXP'),

        ('ACTION_EVENT_HABIT_MOVE_SIMPLE_NOBLE_MONEY', 40026, 'Дневник: В движении, черты, благородство (деньги)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при путешествии благородного героя (деньги)',
         [V.DATE, V.TIME, V.COINS, V.HERO], 'hero#N +coins#G'),

        ('ACTION_EVENT_HABIT_MOVE_SIMPLE_NOBLE_NOTHING', 40027, 'Дневник: В движении, черты, благородство (без бонуса)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при путешествии благородного героя (без бонуса)',
         [V.DATE, V.TIME, V.HERO], None),

        ('ACTION_EVENT_HABIT_MOVE_SIMPLE_PEACEABLE_ARTIFACT', 40028, 'Дневник: В движении, черты, миролюбие (артефакт)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при путешествии миролюбивого героя (артефакт)',
         [V.DATE, V.TIME, V.HERO, V.ARTIFACT], None),

        ('ACTION_EVENT_HABIT_MOVE_SIMPLE_PEACEABLE_EXPERIENCE', 40029, 'Дневник: В движении, черты, миролюбие (опыт)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при путешествии миролюбивого героя (опыт)',
         [V.DATE, V.TIME, V.HERO, V.EXPERIENCE], 'hero#N +experience#EXP'),

        ('ACTION_EVENT_HABIT_MOVE_SIMPLE_PEACEABLE_MONEY', 40030, 'Дневник: В движении, черты, миролюбие (деньги)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при путешествии миролюбивого героя (деньги)',
         [V.DATE, V.TIME, V.COINS, V.HERO], 'hero#N +coins#G'),

        ('ACTION_EVENT_HABIT_MOVE_SIMPLE_PEACEABLE_NOTHING', 40031, 'Дневник: В движении, черты, миролюбие (без бонуса)', relations.LEXICON_GROUP.ACTION_EVENT,
         'События при путешествии миролюбивого героя (без бонуса)',
         [V.DATE, V.TIME, V.HERO], None),

        ]
