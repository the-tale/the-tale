import smart_imports

smart_imports.all()


V = lexicon_relations.VARIABLE


KEYS = [('QUEST_SPYING_ACTION_ARRIVED_TO_TARGET', 560000, 'Активность: герой приехал в город', relations.LEXICON_GROUP.QUEST_SPYING,
         'Краткое суммарное описание действий героя во время приезда в город.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_ACTION_GO_BLACKMAIL', 560001, 'Активность: возвращение для шантажа', relations.LEXICON_GROUP.QUEST_SPYING,
         'Краткое суммарное описание действий героя, когда он возвращается для шантажа.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_ACTION_GO_REPORT_DATA', 560002, 'Активность: возвращение с докладом', relations.LEXICON_GROUP.QUEST_SPYING,
         'Краткое суммарное описание действий героя, когда он возвращается с докладом.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_ACTION_INTRO', 560003, 'Активность: интро', relations.LEXICON_GROUP.QUEST_SPYING,
         'Краткое суммарное описание действий героя в момент получения задания.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_ACTION_MOVE_TO_REPORT_LIE', 560005, 'Активность: герой возвращается, чтобы солгать', relations.LEXICON_GROUP.QUEST_SPYING,
         'Краткое суммарное описание действий героя, когда он возвращается с ложью.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_ACTION_OPEN_UP', 560006, 'Активность: герой «раскрылся»', relations.LEXICON_GROUP.QUEST_SPYING,
         'Краткое суммарное описание действий героя, когда он признаётся цели.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_ACTION_START_OPEN_UP', 560007, 'Активность: начало «раскрытия»', relations.LEXICON_GROUP.QUEST_SPYING,
         'Краткое суммарное описание действий героя при начале раскрытия.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_ACTION_START_SPYING', 560008, 'Активность: начало шпионажа', relations.LEXICON_GROUP.QUEST_SPYING,
         'Краткое суммарное описание действий героя при начале шпионажа.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_ACTION_WITNESS', 560009, 'Активность: погоня за свидетелем', relations.LEXICON_GROUP.QUEST_SPYING,
         'Краткое суммарное описание действий героя во время погони за свидетелем.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_ACTION_WITNESS_FIGHT', 560010, 'Активность: сражение со свидетелем', relations.LEXICON_GROUP.QUEST_SPYING,
         'Краткое суммарное описание действий героя во время сражения со свидетелем.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_ACTOR_INITIATOR', 560011, 'Актёр: инициатор задания', relations.LEXICON_GROUP.QUEST_SPYING,
         'Название роли, инициирующей задание.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_ACTOR_RECEIVER', 560012, 'Актёр: цель слежки', relations.LEXICON_GROUP.QUEST_SPYING,
         'Название роли, цели слежки.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_CHOICE_CURRENT_BLACKMAIL', 560013, 'Выбор: шантаж', relations.LEXICON_GROUP.QUEST_SPYING,
         'Краткая констатация выбора героя в случае шантажа.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_CHOICE_CURRENT_OPEN_UP', 560014, 'Выбор: сдача', relations.LEXICON_GROUP.QUEST_SPYING,
         'Краткая констатация выбора героя в случае сдачи.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_CHOICE_CURRENT_SPY', 560015, 'Выбор: шпионаж', relations.LEXICON_GROUP.QUEST_SPYING,
         'Краткая констатация выбора героя в случае шпионажа.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_CHOICE_VARIANT_BLACKMAIL', 560016, 'Вариант выбора: шантажировать', relations.LEXICON_GROUP.QUEST_SPYING,
         'Краткое описание варианта выбора, ведущего к самостоятельному шантажу.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_CHOICE_VARIANT_OPEN_UP', 560017, 'Вариант выбора: сдаться', relations.LEXICON_GROUP.QUEST_SPYING,
         'Краткое описание варианта выбора, ведущего к отказу от шпионажа.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_CHOICE_VARIANT_SPY', 560018, 'Вариант выбора: шпионить', relations.LEXICON_GROUP.QUEST_SPYING,
         'Краткое описание варианта выбора, ведущего к продолжению шпионажа.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_DIARY_BLACKMAIL', 560019, 'Дневник: шпионить до конца и шантажировать', relations.LEXICON_GROUP.QUEST_SPYING,
         'Герой принял решение воспользоваться полученной информацией в своих целях.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_DIARY_BLACKMAIL_FINISH_ARTIFACT', 560020, 'Дневник: награда при самостоятельном шантаже (артефакт)', relations.LEXICON_GROUP.QUEST_SPYING,
         'Герой получает награду за задание при самостоятельном шантаже (деньги).',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ARTIFACT, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION], None),

        ('QUEST_SPYING_DIARY_BLACKMAIL_FINISH_MONEY', 560021, 'Дневник: награда при самостоятельном шантаже (деньги)', relations.LEXICON_GROUP.QUEST_SPYING,
         'Герой получает награду за задание при самостоятельном шантаже (деньги).',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.COINS, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION], 'hero#N +coins#G'),

        ('QUEST_SPYING_DIARY_INTRO', 560022, 'Дневник: начало задания', relations.LEXICON_GROUP.QUEST_SPYING,
         'Герой получил задание.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_DIARY_MOVE_TO_REPORT_LIE', 560023, 'Дневник: начало путешествия при возвращении ложного отчёта', relations.LEXICON_GROUP.QUEST_SPYING,
         'Герой отправляется к заказчику с ложным отчётом.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION], None),

        ('QUEST_SPYING_DIARY_OPEN_UP', 560024, 'Дневник: решение сдаться', relations.LEXICON_GROUP.QUEST_SPYING,
         'Герой принял решение открыться.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_DIARY_OPEN_UP_FINISH_ARTIFACT', 560025, 'Дневник: награда при сдаче (артефакт)', relations.LEXICON_GROUP.QUEST_SPYING,
         'Герой получает награду за задание при сдаче (артефакт).',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ARTIFACT], None),

        ('QUEST_SPYING_DIARY_OPEN_UP_FINISH_MONEY', 560026, 'Дневник: награда при сдаче (деньги)', relations.LEXICON_GROUP.QUEST_SPYING,
         'Герой получает награду за задание при сдаче (деньги).',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.COINS], 'hero#N +coins#G'),

        ('QUEST_SPYING_DIARY_OPEN_UP_LYING_ARTIFACT', 560027, 'Дневник: награда при сообщении ложной информации (артефакт)', relations.LEXICON_GROUP.QUEST_SPYING,
         'Герой получает награду за задание при сообщении заказчику ложной информации (артефакт).',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ARTIFACT], None),

        ('QUEST_SPYING_DIARY_OPEN_UP_LYING_MONEY', 560028, 'Дневник: награда при сообщении ложной информации (деньги)', relations.LEXICON_GROUP.QUEST_SPYING,
         'Герой получает награду за задание при сообщении заказчику ложной информации (деньги).',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.COINS], 'hero#N +coins#G'),

        ('QUEST_SPYING_DIARY_REPORT_DATA_ARTIFACT', 560029, 'Дневник: награда при шпионаже (артефакт)', relations.LEXICON_GROUP.QUEST_SPYING,
         'Герой получает награду за задание при шпионаже (артефакт).',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ARTIFACT], None),

        ('QUEST_SPYING_DIARY_REPORT_DATA_MONEY', 560030, 'Дневник: награда при шпионаже (деньги)', relations.LEXICON_GROUP.QUEST_SPYING,
         'Герой получает награду за задание при шпионаже (деньги).',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.COINS], 'hero#N +coins#G'),

        ('QUEST_SPYING_DIARY_SUCCESS_SPYING', 560031, 'Дневник: шпионить до конца', relations.LEXICON_GROUP.QUEST_SPYING,
         'Герой принял решение шпионить до конца.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_DIARY_WITNESS', 560032, 'Дневник: героя заметили', relations.LEXICON_GROUP.QUEST_SPYING,
         'Героя заметили во время шпионажа.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_DIARY_WITNESS_FAILED', 560033, 'Дневник: свидетель ушёл от погони (герой убит)', relations.LEXICON_GROUP.QUEST_SPYING,
         'Свидетель скрылся и шпионаж становится бесполезным.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ARTIFACT, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION], None),

        ('QUEST_SPYING_JOURNAL_ARRIVED_TO_TARGET', 560034, 'Журнал: шпионаж', relations.LEXICON_GROUP.QUEST_SPYING,
         'Герой начал шпионить.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_JOURNAL_WITNESS_FIGHT', 560035, 'Журнал: сражение со свидетелем', relations.LEXICON_GROUP.QUEST_SPYING,
         'Герой догнал свидетеля.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_SPYING_NAME', 560036, 'Название', relations.LEXICON_GROUP.QUEST_SPYING,
         'Краткое название задания.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ]
