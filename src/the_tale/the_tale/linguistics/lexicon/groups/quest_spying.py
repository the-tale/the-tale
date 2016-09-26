# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [('QUEST_SPYING_ACTION_ARRIVED_TO_TARGET', 560000, 'Активность: герой приехал в город', LEXICON_GROUP.QUEST_SPYING,
        'Краткое суммарное описание действий героя во время приезда в город.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_ACTION_GO_BLACKMAIL', 560001, 'Активность: возвращение для шантажа', LEXICON_GROUP.QUEST_SPYING,
        'Краткое суммарное описание действий героя, когда он возвращается для шантажа.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_ACTION_GO_REPORT_DATA', 560002, 'Активность: возвращение с докладом', LEXICON_GROUP.QUEST_SPYING,
        'Краткое суммарное описание действий героя, когда он возвращается с докладом.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_ACTION_INTRO', 560003, 'Активность: интро', LEXICON_GROUP.QUEST_SPYING,
        'Краткое суммарное описание действий героя в момент получения задания.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_ACTION_MOVE_TO_REPORT_LIE', 560005, 'Активность: герой возвращается, чтобы солгать', LEXICON_GROUP.QUEST_SPYING,
        'Краткое суммарное описание действий героя, когда он возвращается с ложью.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_ACTION_OPEN_UP', 560006, 'Активность: герой «раскрылся»', LEXICON_GROUP.QUEST_SPYING,
        'Краткое суммарное описание действий героя, когда он признаётся цели.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_ACTION_START_OPEN_UP', 560007, 'Активность: начало «раскрытия»', LEXICON_GROUP.QUEST_SPYING,
        'Краткое суммарное описание действий героя при начале раскрытия.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_ACTION_START_SPYING', 560008, 'Активность: начало шпионажа', LEXICON_GROUP.QUEST_SPYING,
        'Краткое суммарное описание действий героя при начале шпионажа.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_ACTION_WITNESS', 560009, 'Активность: погоня за свидетелем', LEXICON_GROUP.QUEST_SPYING,
        'Краткое суммарное описание действий героя во время погони за свидетелем.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_ACTION_WITNESS_FIGHT', 560010, 'Активность: сражение со свидетелем', LEXICON_GROUP.QUEST_SPYING,
        'Краткое суммарное описание действий героя во время сражения со свидетелем.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_ACTOR_INITIATOR', 560011, 'Актёр: инициатор задания', LEXICON_GROUP.QUEST_SPYING,
        'Название роли, инициирующей задание.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_ACTOR_RECEIVER', 560012, 'Актёр: цель слежки', LEXICON_GROUP.QUEST_SPYING,
        'Название роли, цели слежки.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_CHOICE_CURRENT_BLACKMAIL', 560013, 'Выбор: шантаж', LEXICON_GROUP.QUEST_SPYING,
        'Краткая констатация выбора героя в случае шантажа.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_CHOICE_CURRENT_OPEN_UP', 560014, 'Выбор: сдача', LEXICON_GROUP.QUEST_SPYING,
        'Краткая констатация выбора героя в случае сдачи.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_CHOICE_CURRENT_SPY', 560015, 'Выбор: шпионаж', LEXICON_GROUP.QUEST_SPYING,
        'Краткая констатация выбора героя в случае шпионажа.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_CHOICE_VARIANT_BLACKMAIL', 560016, 'Вариант выбора: шантажировать', LEXICON_GROUP.QUEST_SPYING,
        'Краткое описание варианта выбора, ведущего к самостоятельному шантажу.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_CHOICE_VARIANT_OPEN_UP', 560017, 'Вариант выбора: сдаться', LEXICON_GROUP.QUEST_SPYING,
        'Краткое описание варианта выбора, ведущего к отказу от шпионажа.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_CHOICE_VARIANT_SPY', 560018, 'Вариант выбора: шпионить', LEXICON_GROUP.QUEST_SPYING,
        'Краткое описание варианта выбора, ведущего к продолжению шпионажа.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_DIARY_BLACKMAIL', 560019, 'Дневник: шпионить до конца и шантажировать', LEXICON_GROUP.QUEST_SPYING,
        'Герой принял решение воспользоваться полученной информацией в своих целях.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_DIARY_BLACKMAIL_FINISH_ARTIFACT', 560020, 'Дневник: награда при самостоятельном шантаже (артефакт)', LEXICON_GROUP.QUEST_SPYING,
        'Герой получает награду за задание при самостоятельном шантаже (деньги).',
        [V.INITIATOR, V.HERO, V.ARTIFACT, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION], None),

        ('QUEST_SPYING_DIARY_BLACKMAIL_FINISH_MONEY', 560021, 'Дневник: награда при самостоятельном шантаже (деньги)', LEXICON_GROUP.QUEST_SPYING,
        'Герой получает награду за задание при самостоятельном шантаже (деньги).',
        [V.INITIATOR, V.HERO, V.COINS, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION], 'hero#N +coins#G'),

        ('QUEST_SPYING_DIARY_INTRO', 560022, 'Дневник: начало задания', LEXICON_GROUP.QUEST_SPYING,
        'Герой получил задание.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_DIARY_MOVE_TO_REPORT_LIE', 560023, 'Дневник: начало путешествия при возвращении ложного отчёта', LEXICON_GROUP.QUEST_SPYING,
        'Герой отправляется к заказчику с ложным отчётом.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION], None),

        ('QUEST_SPYING_DIARY_OPEN_UP', 560024, 'Дневник: решение сдаться', LEXICON_GROUP.QUEST_SPYING,
        'Герой принял решение открыться.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_DIARY_OPEN_UP_FINISH_ARTIFACT', 560025, 'Дневник: награда при сдаче (артефакт)', LEXICON_GROUP.QUEST_SPYING,
        'Герой получает награду за задание при сдаче (артефакт).',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ARTIFACT], None),

        ('QUEST_SPYING_DIARY_OPEN_UP_FINISH_MONEY', 560026, 'Дневник: награда при сдаче (деньги)', LEXICON_GROUP.QUEST_SPYING,
        'Герой получает награду за задание при сдаче (деньги).',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.COINS], 'hero#N +coins#G'),

        ('QUEST_SPYING_DIARY_OPEN_UP_LYING_ARTIFACT', 560027, 'Дневник: награда при сообщении ложной информации (артефакт)', LEXICON_GROUP.QUEST_SPYING,
        'Герой получает награду за задание при сообщении заказчику ложной информации (артефакт).',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ARTIFACT], None),

        ('QUEST_SPYING_DIARY_OPEN_UP_LYING_MONEY', 560028, 'Дневник: награда при сообщении ложной информации (деньги)', LEXICON_GROUP.QUEST_SPYING,
        'Герой получает награду за задание при сообщении заказчику ложной информации (деньги).',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.COINS], 'hero#N +coins#G'),

        ('QUEST_SPYING_DIARY_REPORT_DATA_ARTIFACT', 560029, 'Дневник: награда при шпионаже (артефакт)', LEXICON_GROUP.QUEST_SPYING,
        'Герой получает награду за задание при шпионаже (артефакт).',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ARTIFACT], None),

        ('QUEST_SPYING_DIARY_REPORT_DATA_MONEY', 560030, 'Дневник: награда при шпионаже (деньги)', LEXICON_GROUP.QUEST_SPYING,
        'Герой получает награду за задание при шпионаже (деньги).',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.COINS], 'hero#N +coins#G'),

        ('QUEST_SPYING_DIARY_SUCCESS_SPYING', 560031, 'Дневник: шпионить до конца', LEXICON_GROUP.QUEST_SPYING,
        'Герой принял решение шпионить до конца.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_DIARY_WITNESS', 560032, 'Дневник: героя заметили', LEXICON_GROUP.QUEST_SPYING,
        'Героя заметили во время шпионажа.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_DIARY_WITNESS_FAILED', 560033, 'Дневник: свидетель ушёл от погони (герой убит)', LEXICON_GROUP.QUEST_SPYING,
        'Свидетель скрылся и шпионаж становится беспользеным.',
        [V.INITIATOR, V.HERO, V.ARTIFACT, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION], None),

        ('QUEST_SPYING_JOURNAL_ARRIVED_TO_TARGET', 560034, 'Журнал: шпионаж', LEXICON_GROUP.QUEST_SPYING,
        'Герой начал шпионить.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_JOURNAL_WITNESS_FIGHT', 560035, 'Журнал: сражение со свидетелем', LEXICON_GROUP.QUEST_SPYING,
        'Герой догнал свидетеля.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_NAME', 560036, 'Название', LEXICON_GROUP.QUEST_SPYING,
        'Краткое название задания.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ]
