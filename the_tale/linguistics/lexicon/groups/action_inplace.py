# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'ACTION_INPLACE_DESCRIPTION', 80000, u'Описание', LEXICON_GROUP.ACTION_INPLACE,
        u'Краткая декларация того, что делает герой.',
        [V.HERO, V.PLACE]),

        (u'ACTION_INPLACE_DIARY_BUYING_ARTIFACT', 80001, u'Дневник: Покупка артефакта', LEXICON_GROUP.ACTION_INPLACE,
        u'Герой тратит деньги на покупку артефакта, который будет экипироваться в первый раз (т.е. слот для него не занят другим артефактом).',
        [V.COINS, V.HERO, V.ARTIFACT]),

        (u'ACTION_INPLACE_DIARY_BUYING_ARTIFACT_AND_CHANGE', 80002, u'Дневник: Покупка артефакта и замена', LEXICON_GROUP.ACTION_INPLACE,
        u'Герой тратит деньги на покупку артефакта, и меняет на него экипированный ранее.',
        [V.SELL_PRICE, V.HERO, V.COINS_DELTA, V.OLD_ARTIFACT, V.COINS, V.ARTIFACT]),

        (u'ACTION_INPLACE_DIARY_BUYING_ARTIFACT_AND_CHANGE_EQUAL_ITEMS', 80003, u'Дневник: Покупка аналогичного артефакта и замена', LEXICON_GROUP.ACTION_INPLACE,
        u'Герой тратит деньги на покупку нового, но аналогичного уже экипированному, артефакта, и меняет на него экипированный ранее.',
        [V.SELL_PRICE, V.COINS, V.HERO, V.ARTIFACT, V.COINS_DELTA]),

        (u'ACTION_INPLACE_DIARY_EXPERIENCE', 80004, u'Дневник: Обучение', LEXICON_GROUP.ACTION_INPLACE,
        u'Герой тратит деньги, чтобы немного подучиться',
        [V.COINS, V.HERO, V.EXPERIENCE]),

        (u'ACTION_INPLACE_DIARY_IMPACT_BAD', 80005, u'Дневник: Вредительство жителю', LEXICON_GROUP.ACTION_INPLACE,
        u'Герой тратит деньги, чтобы навредить жителю города',
        [V.PERSON, V.COINS, V.HERO]),

        (u'ACTION_INPLACE_DIARY_IMPACT_GOOD', 80006, u'Дневник: Помощь жителю', LEXICON_GROUP.ACTION_INPLACE,
        u'Герой тратит деньги на помощь жителю города.',
        [V.PERSON, V.COINS, V.HERO]),

        (u'ACTION_INPLACE_DIARY_INSTANT_HEAL_FOR_MONEY', 80007, u'Дневник: Лечение за деньги', LEXICON_GROUP.ACTION_INPLACE,
        u'Герой тратит деньги на лечение.',
        [V.COINS, V.HERO]),

        (u'ACTION_INPLACE_DIARY_REPAIRING_ARTIFACT', 80008, u'Дневник: починка артефакта', LEXICON_GROUP.ACTION_INPLACE,
        u'Герой тратит деньги на починку артефакта.',
        [V.COINS, V.HERO, V.ARTIFACT]),

        (u'ACTION_INPLACE_DIARY_SHARPENING_ARTIFACT', 80009, u'Дневник: Заточка артефакта', LEXICON_GROUP.ACTION_INPLACE,
        u'Герой тратит деньги на заточку артефакта.',
        [V.COINS, V.HERO, V.ARTIFACT]),

        (u'ACTION_INPLACE_DIARY_SPEND_USELESS', 80010, u'Дневник: Бесполезные траты', LEXICON_GROUP.ACTION_INPLACE,
        u'Герой тратит деньги на бесполезную вещь или занятие.',
        [V.COINS, V.HERO]),

        (u'ACTION_INPLACE_HABIT_EVENT_HONOR_LEFT_1', 80011, u'Дневник: запись о характере города (Честь: уровень -1)', LEXICON_GROUP.ACTION_INPLACE,
        u'запись о характере города (Честь: уровень -3)',
        [V.HERO, V.PLACE]),

        (u'ACTION_INPLACE_HABIT_EVENT_HONOR_LEFT_2', 80012, u'Дневник: запись о характере города (Честь: уровень -2)', LEXICON_GROUP.ACTION_INPLACE,
        u'запись о характере города (Честь: уровень -2)',
        [V.HERO, V.PLACE]),

        (u'ACTION_INPLACE_HABIT_EVENT_HONOR_LEFT_3', 80013, u'Дневник: запись о характере города (Честь: уровень -3)', LEXICON_GROUP.ACTION_INPLACE,
        u'запись о характере города (Честь: уровень -3)',
        [V.HERO, V.PLACE]),

        (u'ACTION_INPLACE_HABIT_EVENT_HONOR_NEUTRAL', 80014, u'Дневник: запись о характере города (Честь: нейтральное значение)', LEXICON_GROUP.ACTION_INPLACE,
        u'запись о характере города (Честь: нейтральное значение)',
        [V.HERO, V.PLACE]),

        (u'ACTION_INPLACE_HABIT_EVENT_HONOR_RIGHT_1', 80015, u'Дневник: запись о характере города (Честь: уровень 1)', LEXICON_GROUP.ACTION_INPLACE,
        u'запись о характере города (Честь: уровень 1)',
        [V.HERO, V.PLACE]),

        (u'ACTION_INPLACE_HABIT_EVENT_HONOR_RIGHT_2', 80016, u'Дневник: запись о характере города (Честь: уровень 2)', LEXICON_GROUP.ACTION_INPLACE,
        u'запись о характере города (Честь: уровень 2)',
        [V.HERO, V.PLACE]),

        (u'ACTION_INPLACE_HABIT_EVENT_HONOR_RIGHT_3', 80017, u'Дневник: запись о характере города (Честь: уровень 3)', LEXICON_GROUP.ACTION_INPLACE,
        u'запись о характере города (Честь: уровень 3)',
        [V.HERO, V.PLACE]),

        (u'ACTION_INPLACE_HABIT_EVENT_PEACEFULNESS_LEFT_1', 80018, u'Дневник: запись о характере города (Миролюбие: уровень -1)', LEXICON_GROUP.ACTION_INPLACE,
        u'запись о характере города (Миролюбие: уровень -1)',
        [V.HERO, V.PLACE]),

        (u'ACTION_INPLACE_HABIT_EVENT_PEACEFULNESS_LEFT_2', 80019, u'Дневник: запись о характере города (Миролюбие: уровень -2)', LEXICON_GROUP.ACTION_INPLACE,
        u'запись о характере города (Миролюбие: уровень -2)',
        [V.HERO, V.PLACE]),

        (u'ACTION_INPLACE_HABIT_EVENT_PEACEFULNESS_LEFT_3', 80020, u'Дневник: запись о характере города (Миролюбие: уровень -3)', LEXICON_GROUP.ACTION_INPLACE,
        u'запись о характере города (Миролюбие: уровень -3)',
        [V.HERO, V.PLACE]),

        (u'ACTION_INPLACE_HABIT_EVENT_PEACEFULNESS_NEUTRAL', 80021, u'Дневник: запись о характере города (Миролюбие: нейтральное значение)', LEXICON_GROUP.ACTION_INPLACE,
        u'запись о характере города (Миролюбие: нейтральное значение)',
        [V.HERO, V.PLACE]),

        (u'ACTION_INPLACE_HABIT_EVENT_PEACEFULNESS_RIGHT_1', 80022, u'Дневник: запись о характере города (Миролюбие: уровень 1)', LEXICON_GROUP.ACTION_INPLACE,
        u'запись о характере города (Миролюбие: уровень 1)',
        [V.HERO, V.PLACE]),

        (u'ACTION_INPLACE_HABIT_EVENT_PEACEFULNESS_RIGHT_2', 80023, u'Дневник: запись о характере города (Миролюбие: уровень 2)', LEXICON_GROUP.ACTION_INPLACE,
        u'запись о характере города (Миролюбие: уровень 2)',
        [V.HERO, V.PLACE]),

        (u'ACTION_INPLACE_HABIT_EVENT_PEACEFULNESS_RIGHT_3', 80024, u'Дневник: запись о характере города (Миролюбие: уровень 3)', LEXICON_GROUP.ACTION_INPLACE,
        u'запись о характере города (Миролюбие: уровень 3)',
        [V.HERO, V.PLACE]),

        (u'ACTION_INPLACE_INSTANT_ENERGY_REGEN', 80025, u'Журнал: Восстановление энергии в святом городе', LEXICON_GROUP.ACTION_INPLACE,
        u'Игрок восстанавливает немного энергии, когда герой посещает город.',
        [V.HERO, V.PLACE]),

        (u'ACTION_INPLACE_INSTANT_HEAL', 80026, u'Журнал: Лечение в курорте', LEXICON_GROUP.ACTION_INPLACE,
        u'Герой моментально излечивается благодаря типу города «Курорт».',
        [V.HERO, V.PLACE]),

        (u'ACTION_INPLACE_TAX', 80027, u'Дневник: Оплата пошлины при входе в город', LEXICON_GROUP.ACTION_INPLACE,
        u'Герой платит процент от своего золота при входе в город.',
        [V.HERO, V.COINS, V.PLACE]),

        (u'ACTION_INPLACE_TAX_NO_MONEY', 80028, u'Дневник: взимание пошлины', LEXICON_GROUP.ACTION_INPLACE,
        u'Герой платит пошлину за посещение города.',
        [V.HERO, V.PLACE]),

        (u'ACTION_INPLACE_COMPANION_HEAL', 80029, u'Журнал: Лечение спутника в курорте', LEXICON_GROUP.ACTION_INPLACE,
        u'Спутник восстанавливает 1 здоровья благодаря типу города «Курорт».',
        [V.HERO, V.PLACE, V.COMPANION]),

        (u'ACTION_INPLACE_COMPANION_STEAL_MONEY', 80030, u'Журнал: Спутник украл немного денег', LEXICON_GROUP.ACTION_INPLACE,
        u'Спутник украл немного денег.',
        [V.HERO, V.PLACE, V.COMPANION, V.COINS]),

        (u'ACTION_INPLACE_COMPANION_STEAL_ITEM', 80031, u'Журнал: Спутник украл предмет', LEXICON_GROUP.ACTION_INPLACE,
        u'Спутник спутник украл предмет.',
        [V.HERO, V.PLACE, V.COMPANION, V.ARTIFACT]),

        (u'ACTION_INPLACE_COMPANION_MONEY_FOR_FOOD', 80032, u'Журнал: Герой приобрёл еду для спутника', LEXICON_GROUP.ACTION_INPLACE,
        u'Герой приобрёт еду для спутника.',
        [V.HERO, V.PLACE, V.COMPANION, V.COINS]),

        (u'ACTION_INPLACE_COMPANION_DRINK_ARTIFACT', 80033, u'Журнал: Спутник пропил предмет из рюкзака героя', LEXICON_GROUP.ACTION_INPLACE,
        u'Спутник пропивает предмет из рюкзака героя. Особенность «пьяница».',
        [V.HERO, V.PLACE, V.COMPANION, V.ARTIFACT]),

        (u'ACTION_INPLACE_COMPANION_LEAVE', 80034, u'Дневник: Спутник покинул героя из-за способности «нелюдимый»', LEXICON_GROUP.ACTION_INPLACE,
        u'Спутник покинул героя из-за способности «нелюдимый».',
        [V.HERO, V.PLACE, V.COMPANION]),
        ]
