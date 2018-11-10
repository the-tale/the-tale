

import smart_imports

smart_imports.all()


V = lexicon_relations.VARIABLE


KEYS = [('QUEST_COLLECT_DEBT_ACTION_AFTER_FAILED_HELP', 380000, 'Активность: после провала задания', relations.LEXICON_GROUP.QUEST_COLLECT_DEBT,
         'Краткое суммарное описание действий героя после провала задания помощи.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_COLLECT_DEBT_ACTION_AFTER_SUCCESSED_HELP', 380001, 'Активность: после выполнения задания', relations.LEXICON_GROUP.QUEST_COLLECT_DEBT,
         'Краткое суммарное описание действий героя после удачного выполнения задания.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_COLLECT_DEBT_ACTION_ATTACK', 380002, 'Активность: выбивание долга', relations.LEXICON_GROUP.QUEST_COLLECT_DEBT,
         'Краткое суммарное описание действий героя во время выбивания долга.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_COLLECT_DEBT_ACTION_ATTACK_FAILED', 380003, 'Активность: герой умер и не смог выбить долг', relations.LEXICON_GROUP.QUEST_COLLECT_DEBT,
         'Краткое суммарное описание действий героя после неудачи в выбивании долга.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_COLLECT_DEBT_ACTION_ATTACK_SUCCESSED', 380004, 'Активность: герой успешно выбил долг', relations.LEXICON_GROUP.QUEST_COLLECT_DEBT,
         'Краткое суммарное описание действий героя, когда он начинает путь за наградой.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_COLLECT_DEBT_ACTION_BEFORE_HELP', 380005, 'Активность: герой помогает должнику', relations.LEXICON_GROUP.QUEST_COLLECT_DEBT,
         'Краткое суммарное описание действий героя во время помощи должнику.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_COLLECT_DEBT_ACTION_INTRO', 380006, 'Активность: интро', relations.LEXICON_GROUP.QUEST_COLLECT_DEBT,
         'Краткое суммарное описание действий героя в момент получения задания.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_COLLECT_DEBT_ACTOR_INITIATOR', 380007, 'Актёр: Инициатор задания', relations.LEXICON_GROUP.QUEST_COLLECT_DEBT,
         'Название роли, инициирующей задание.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_COLLECT_DEBT_ACTOR_RECEIVER', 380008, 'Актёр: должник', relations.LEXICON_GROUP.QUEST_COLLECT_DEBT,
         'Название роли, должник.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_COLLECT_DEBT_CHOICE_CURRENT_ATTACK', 380009, 'Выбор: насилие', relations.LEXICON_GROUP.QUEST_COLLECT_DEBT,
         'Краткая констатация выбора героя в случае насилия.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_COLLECT_DEBT_CHOICE_CURRENT_HELP', 380010, 'Выбор: помощь', relations.LEXICON_GROUP.QUEST_COLLECT_DEBT,
         'Краткая констатация выбора героя в случае помощи.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_COLLECT_DEBT_CHOICE_VARIANT_ATTACK', 380011, 'Вариант выбора: насилие', relations.LEXICON_GROUP.QUEST_COLLECT_DEBT,
         'Краткое описание варианта выбора, ведущего к силовому решению.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_COLLECT_DEBT_CHOICE_VARIANT_HELP', 380012, 'Вариант выбора: помощь', relations.LEXICON_GROUP.QUEST_COLLECT_DEBT,
         'Краткое описание варианта выбора, ведущего к помощи должнику.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_COLLECT_DEBT_DIARY_AFTER_FAILED_HELP', 380013, 'Дневник: выбивание долга после провала задания', relations.LEXICON_GROUP.QUEST_COLLECT_DEBT,
         'Герой решает заставить должника силой после того, как не смог выполнить его задание',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_COLLECT_DEBT_DIARY_ATTACK', 380014, 'Дневник: выбор насилия', relations.LEXICON_GROUP.QUEST_COLLECT_DEBT,
         'Герой решает заставить должника силой',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_COLLECT_DEBT_DIARY_BEFORE_HELP', 380015, 'Дневник: выбор помощи', relations.LEXICON_GROUP.QUEST_COLLECT_DEBT,
         'Герой решает помочь должнику',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_COLLECT_DEBT_DIARY_FINISH_ATTACK_FAILED', 380016, 'Дневник: должник оказался сильнее', relations.LEXICON_GROUP.QUEST_COLLECT_DEBT,
         'Герой не смог силой заставить должника выполнить обещание.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.COINS], 'hero#N'),

        ('QUEST_COLLECT_DEBT_DIARY_FINISH_ATTACK_SUCCESSED_ARTIFACT', 380017, 'Дневник: награда за успешное применение насилия (артефакт)', relations.LEXICON_GROUP.QUEST_COLLECT_DEBT,
         'Герой получает награду за успешное применение насилия (артефакт).',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ARTIFACT], None),

        ('QUEST_COLLECT_DEBT_DIARY_FINISH_ATTACK_SUCCESSED_MONEY', 380018, 'Дневник: награда за успешное применение насилия (деньги)', relations.LEXICON_GROUP.QUEST_COLLECT_DEBT,
         'Герой получает награду за успешное применение насилия (деньги).',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.COINS], 'hero#N +coins#G'),

        ('QUEST_COLLECT_DEBT_DIARY_FINISH_HELP_ARTIFACT', 380019, 'Дневник: награда за задание (артефакт)', relations.LEXICON_GROUP.QUEST_COLLECT_DEBT,
         'Герой получает награду за выполнение задания (артефакт).',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ARTIFACT], None),

        ('QUEST_COLLECT_DEBT_DIARY_FINISH_HELP_MONEY', 380020, 'Дневник: награда за задание (деньги)', relations.LEXICON_GROUP.QUEST_COLLECT_DEBT,
         'Герой получает награду за выполнение задания (деньги).',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.COINS], 'hero#N +coins#G'),

        ('QUEST_COLLECT_DEBT_DIARY_INTRO', 380021, 'Дневник: начало задания', relations.LEXICON_GROUP.QUEST_COLLECT_DEBT,
         'Герой получил задание.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_COLLECT_DEBT_JOURNAL_FINISH', 380022, 'Журнал: возвращение', relations.LEXICON_GROUP.QUEST_COLLECT_DEBT,
         'Герой возвращается за наградой.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_COLLECT_DEBT_JOURNAL_MOVE_TO_RECEIVER', 380023, 'Журнал: начало путешествия к должнику', relations.LEXICON_GROUP.QUEST_COLLECT_DEBT,
         'Герой отправляется к должнику.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_COLLECT_DEBT_NAME', 380024, 'Название', relations.LEXICON_GROUP.QUEST_COLLECT_DEBT,
         'Краткое название задания.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ]
