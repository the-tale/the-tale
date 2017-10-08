
from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [('ACTION_INPLACE_DESCRIPTION', 80000, 'Описание', LEXICON_GROUP.ACTION_INPLACE,
        'Краткая декларация того, что делает герой.',
        [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_INPLACE_DIARY_BUYING_ARTIFACT', 80001, 'Дневник: Покупка артефакта', LEXICON_GROUP.ACTION_INPLACE,
        'Герой тратит деньги на покупку артефакта, который будет экипироваться в первый раз (т.е. слот для него не занят другим артефактом).',
        [V.DATE, V.TIME, V.COINS, V.HERO, V.ARTIFACT], None),

        ('ACTION_INPLACE_DIARY_BUYING_ARTIFACT_AND_CHANGE', 80002, 'Дневник: Покупка артефакта и замена', LEXICON_GROUP.ACTION_INPLACE,
        'Герой тратит деньги на покупку артефакта, и меняет на него экипированный ранее. Старая экипировка продаётся, деньги с продажи остаются у героя.',
        [V.DATE, V.TIME, V.SELL_PRICE, V.HERO, V.OLD_ARTIFACT, V.COINS, V.ARTIFACT], 'hero#N -coins#G +sell_price#G'),

        ('ACTION_INPLACE_DIARY_BUYING_ARTIFACT_AND_CHANGE_EQUAL_ITEMS', 80003, 'Дневник: Покупка аналогичного артефакта и замена', LEXICON_GROUP.ACTION_INPLACE,
        'Герой тратит деньги на покупку нового, но аналогичного уже экипированному, артефакта, и меняет на него экипированный ранее. Старая экипировка продаётся, деньги с продажи остаются у героя.',
        [V.DATE, V.TIME, V.SELL_PRICE, V.COINS, V.HERO, V.ARTIFACT], 'hero#N -coins#G +sell_price#G'),

        ('ACTION_INPLACE_DIARY_EXPERIENCE', 80004, 'Дневник: Траты на обучение', LEXICON_GROUP.ACTION_INPLACE,
        'Герой тратит деньги, чтобы немного подучиться',
        [V.DATE, V.TIME, V.COINS, V.HERO, V.EXPERIENCE], 'hero#N -coins#G +experience#EXP'),

        ('ACTION_INPLACE_DIARY_IMPACT_BAD', 80005, 'Дневник: Траты на вредительство жителю', LEXICON_GROUP.ACTION_INPLACE,
        'Герой тратит деньги, чтобы навредить жителю города',
        [V.DATE, V.TIME, V.PERSON, V.COINS, V.HERO], 'hero#N -coins#G'),

        ('ACTION_INPLACE_DIARY_IMPACT_GOOD', 80006, 'Дневник: Траты на помощь жителю', LEXICON_GROUP.ACTION_INPLACE,
        'Герой тратит деньги на помощь жителю города.',
        [V.DATE, V.TIME, V.PERSON, V.COINS, V.HERO], 'hero#N -coins#G'),

        ('ACTION_INPLACE_DIARY_INSTANT_HEAL_FOR_MONEY', 80007, 'Дневник: Траты на лечение', LEXICON_GROUP.ACTION_INPLACE,
        'Герой тратит деньги на лечение.',
        [V.DATE, V.TIME, V.COINS, V.HERO, V.HEALTH], 'hero#N +health#HP -coins#G'),

        ('ACTION_INPLACE_DIARY_REPAIRING_ARTIFACT', 80008, 'Дневник: Траты на починку артефакта', LEXICON_GROUP.ACTION_INPLACE,
        'Герой тратит деньги на починку артефакта.',
        [V.DATE, V.TIME, V.COINS, V.HERO, V.ARTIFACT], 'hero#N -coins#G'),

        ('ACTION_INPLACE_DIARY_SHARPENING_ARTIFACT', 80009, 'Дневник: Траты на заточку артефакта', LEXICON_GROUP.ACTION_INPLACE,
        'Герой тратит деньги на заточку артефакта.',
        [V.DATE, V.TIME, V.COINS, V.HERO, V.ARTIFACT], 'hero#N -coins#G'),

        ('ACTION_INPLACE_DIARY_SPEND_USELESS', 80010, 'Дневник: Траты на себя', LEXICON_GROUP.ACTION_INPLACE,
        'Герой тратит деньги на удовлетворение своих, не обязательно полезных, желаний.',
        [V.DATE, V.TIME, V.COINS, V.HERO], 'hero#N -coins#G'),

        ('ACTION_INPLACE_HABIT_EVENT_HONOR_LEFT_1', 80011, 'Дневник: запись о характере города (Честь: уровень -1)', LEXICON_GROUP.ACTION_INPLACE,
        'запись о характере города (Честь: уровень -1)',
        [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_INPLACE_HABIT_EVENT_HONOR_LEFT_2', 80012, 'Дневник: запись о характере города (Честь: уровень -2)', LEXICON_GROUP.ACTION_INPLACE,
        'запись о характере города (Честь: уровень -2)',
        [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_INPLACE_HABIT_EVENT_HONOR_LEFT_3', 80013, 'Дневник: запись о характере города (Честь: уровень -3)', LEXICON_GROUP.ACTION_INPLACE,
        'запись о характере города (Честь: уровень -3)',
        [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_INPLACE_HABIT_EVENT_HONOR_NEUTRAL', 80014, 'Дневник: запись о характере города (Честь: нейтральное значение)', LEXICON_GROUP.ACTION_INPLACE,
        'запись о характере города (Честь: нейтральное значение)',
        [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_INPLACE_HABIT_EVENT_HONOR_RIGHT_1', 80015, 'Дневник: запись о характере города (Честь: уровень 1)', LEXICON_GROUP.ACTION_INPLACE,
        'запись о характере города (Честь: уровень 1)',
        [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_INPLACE_HABIT_EVENT_HONOR_RIGHT_2', 80016, 'Дневник: запись о характере города (Честь: уровень 2)', LEXICON_GROUP.ACTION_INPLACE,
        'запись о характере города (Честь: уровень 2)',
        [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_INPLACE_HABIT_EVENT_HONOR_RIGHT_3', 80017, 'Дневник: запись о характере города (Честь: уровень 3)', LEXICON_GROUP.ACTION_INPLACE,
        'запись о характере города (Честь: уровень 3)',
        [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_INPLACE_HABIT_EVENT_PEACEFULNESS_LEFT_1', 80018, 'Дневник: запись о характере города (Миролюбие: уровень -1)', LEXICON_GROUP.ACTION_INPLACE,
        'запись о характере города (Миролюбие: уровень -1)',
        [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_INPLACE_HABIT_EVENT_PEACEFULNESS_LEFT_2', 80019, 'Дневник: запись о характере города (Миролюбие: уровень -2)', LEXICON_GROUP.ACTION_INPLACE,
        'запись о характере города (Миролюбие: уровень -2)',
        [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_INPLACE_HABIT_EVENT_PEACEFULNESS_LEFT_3', 80020, 'Дневник: запись о характере города (Миролюбие: уровень -3)', LEXICON_GROUP.ACTION_INPLACE,
        'запись о характере города (Миролюбие: уровень -3)',
        [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_INPLACE_HABIT_EVENT_PEACEFULNESS_NEUTRAL', 80021, 'Дневник: запись о характере города (Миролюбие: нейтральное значение)', LEXICON_GROUP.ACTION_INPLACE,
        'запись о характере города (Миролюбие: нейтральное значение)',
        [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_INPLACE_HABIT_EVENT_PEACEFULNESS_RIGHT_1', 80022, 'Дневник: запись о характере города (Миролюбие: уровень 1)', LEXICON_GROUP.ACTION_INPLACE,
        'запись о характере города (Миролюбие: уровень 1)',
        [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_INPLACE_HABIT_EVENT_PEACEFULNESS_RIGHT_2', 80023, 'Дневник: запись о характере города (Миролюбие: уровень 2)', LEXICON_GROUP.ACTION_INPLACE,
        'запись о характере города (Миролюбие: уровень 2)',
        [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_INPLACE_HABIT_EVENT_PEACEFULNESS_RIGHT_3', 80024, 'Дневник: запись о характере города (Миролюбие: уровень 3)', LEXICON_GROUP.ACTION_INPLACE,
        'запись о характере города (Миролюбие: уровень 3)',
        [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_INPLACE_INSTANT_ENERGY_REGEN', 80025, 'Журнал: Восстановление энергии в святом городе', LEXICON_GROUP.ACTION_INPLACE,
        'Игрок восстанавливает немного энергии, когда герой посещает город.',
        [V.DATE, V.TIME, V.HERO, V.PLACE, V.ENERGY], 'hero#N +energy#EN'),

        ('ACTION_INPLACE_INSTANT_HEAL', 80026, 'Журнал: Лечение в курорте', LEXICON_GROUP.ACTION_INPLACE,
        'Герой моментально излечивается благодаря типу города «Курорт».',
        [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_INPLACE_TAX', 80027, 'Дневник: Оплата пошлины при входе в город', LEXICON_GROUP.ACTION_INPLACE,
        'Герой платит процент от своего золота при входе в город.',
        [V.DATE, V.TIME, V.HERO, V.COINS, V.PLACE], 'hero#N -coins#G'),

        ('ACTION_INPLACE_TAX_NO_MONEY', 80028, 'Дневник: Нет денег на пошлину', LEXICON_GROUP.ACTION_INPLACE,
        'У героя нет денег, чтобы заплатить пошлину, поэтому он проходит в город бесплатно.',
        [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_INPLACE_COMPANION_HEAL', 80029, 'Журнал: Лечение спутника в курорте', LEXICON_GROUP.ACTION_INPLACE,
        'Спутник восстанавливает 1 здоровья благодаря типу города «Курорт».',
        [V.DATE, V.TIME, V.HERO, V.PLACE, V.COMPANION, V.HEALTH], 'companion#N +health#HP'),

        ('ACTION_INPLACE_COMPANION_STEAL_MONEY', 80030, 'Журнал: Спутник украл немного денег', LEXICON_GROUP.ACTION_INPLACE,
        'Спутник украл немного денег.',
        [V.DATE, V.TIME, V.HERO, V.PLACE, V.COMPANION, V.COINS], 'hero#N +coins#G'),

        ('ACTION_INPLACE_COMPANION_STEAL_ITEM', 80031, 'Журнал: Спутник украл предмет', LEXICON_GROUP.ACTION_INPLACE,
        'Спутник украл предмет.',
        [V.DATE, V.TIME, V.HERO, V.PLACE, V.COMPANION, V.ARTIFACT], None),

        ('ACTION_INPLACE_COMPANION_MONEY_FOR_FOOD', 80032, 'Журнал: Герой приобрёл еду для спутника', LEXICON_GROUP.ACTION_INPLACE,
        'Герой приобрёт еду для спутника.',
        [V.DATE, V.TIME, V.HERO, V.PLACE, V.COMPANION, V.COINS], 'hero#N -coins#G'),

        ('ACTION_INPLACE_COMPANION_DRINK_ARTIFACT', 80033, 'Журнал: Спутник пропил предмет из рюкзака героя', LEXICON_GROUP.ACTION_INPLACE,
        'Спутник пропивает предмет из рюкзака героя. Особенность «пьяница».',
        [V.DATE, V.TIME, V.HERO, V.PLACE, V.COMPANION, V.ARTIFACT], None),

        ('ACTION_INPLACE_COMPANION_LEAVE', 80034, 'Дневник: Спутник покинул героя из-за способности «нелюдимый»', LEXICON_GROUP.ACTION_INPLACE,
        'Спутник покинул героя из-за способности «нелюдимый».',
        [V.DATE, V.TIME, V.HERO, V.PLACE, V.COMPANION], None),

        ('ACTION_INPLACE_DIARY_HEAL_COMPANION_HEALED', 80035, 'Дневник: Лечение спутника', LEXICON_GROUP.ACTION_INPLACE,
        'Герой восстановил спутнику немного здоровья, потратив деньги.',
        [V.DATE, V.TIME, V.HERO, V.PLACE, V.COMPANION, V.COINS, V.HEALTH], 'hero#N -coins#G companion#N +health#HP'),

        ('ACTION_INPLACE_ENTER', 80036, 'Журнал: Герой входит в город', LEXICON_GROUP.ACTION_INPLACE,
         'Описание того как герой входит в город.',
         [V.DATE, V.TIME, V.HERO, V.PLACE], None),
        ]
