# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'QUEST_COLLECT_DEBT_ACTION_AFTER_FAILED_HELP', 380000, u'Активность: после провала задания', LEXICON_GROUP.QUEST_COLLECT_DEBT,
        u'Краткое суммарное описание действий героя после провала задания помощи.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION]),

        (u'QUEST_COLLECT_DEBT_ACTION_AFTER_SUCCESSED_HELP', 380001, u'Активность: после выполнения задания', LEXICON_GROUP.QUEST_COLLECT_DEBT,
        u'Краткое суммарное описание действий героя после удачного выполнения задания.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION]),

        (u'QUEST_COLLECT_DEBT_ACTION_ATTACK', 380002, u'Активность: выбивание долга', LEXICON_GROUP.QUEST_COLLECT_DEBT,
        u'Краткое суммарное описание действий героя во время выбивания долга.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION]),

        (u'QUEST_COLLECT_DEBT_ACTION_ATTACK_FAILED', 380003, u'Активность: герой умер и не смог выбить долг', LEXICON_GROUP.QUEST_COLLECT_DEBT,
        u'Краткое суммарное описание действий героя после неудачи в выбивании долга.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION]),

        (u'QUEST_COLLECT_DEBT_ACTION_ATTACK_SUCCESSED', 380004, u'Активность: герой успешно выбил долг', LEXICON_GROUP.QUEST_COLLECT_DEBT,
        u'Краткое суммарное описание действий героя, когда он начинает путь за наградой.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION]),

        (u'QUEST_COLLECT_DEBT_ACTION_BEFORE_HELP', 380005, u'Активность: герой помогает должнику', LEXICON_GROUP.QUEST_COLLECT_DEBT,
        u'Краткое суммарное описание действий героя во время помощи должнику.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION]),

        (u'QUEST_COLLECT_DEBT_ACTION_INTRO', 380006, u'Активность: интро', LEXICON_GROUP.QUEST_COLLECT_DEBT,
        u'Краткое суммарное описание действий героя в момент получения задания.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION]),

        (u'QUEST_COLLECT_DEBT_ACTOR_INITIATOR', 380007, u'Актёр: Инициатор задания', LEXICON_GROUP.QUEST_COLLECT_DEBT,
        u'Название роли, инициирующей задание.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION]),

        (u'QUEST_COLLECT_DEBT_ACTOR_RECEIVER', 380008, u'Актёр: должник', LEXICON_GROUP.QUEST_COLLECT_DEBT,
        u'Название роли, должник.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION]),

        (u'QUEST_COLLECT_DEBT_CHOICE_CURRENT_ATTACK', 380009, u'Выбор: насилие', LEXICON_GROUP.QUEST_COLLECT_DEBT,
        u'Краткая констатация выбора героя в случае насилия.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION]),

        (u'QUEST_COLLECT_DEBT_CHOICE_CURRENT_HELP', 380010, u'Выбор: помощь', LEXICON_GROUP.QUEST_COLLECT_DEBT,
        u'Краткая констатация выбора героя в случае помощи.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION]),

        (u'QUEST_COLLECT_DEBT_CHOICE_VARIANT_ATTACK', 380011, u'Вариант выбора: насилие', LEXICON_GROUP.QUEST_COLLECT_DEBT,
        u'Краткое описание варианта выбора, ведущего к силовому решению.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION]),

        (u'QUEST_COLLECT_DEBT_CHOICE_VARIANT_HELP', 380012, u'Вариант выбора: помощь', LEXICON_GROUP.QUEST_COLLECT_DEBT,
        u'Краткое описание варианта выбора, ведущего к помощи должнику.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION]),

        (u'QUEST_COLLECT_DEBT_DIARY_AFTER_FAILED_HELP', 380013, u'Дневник: выбивание долга после провала задания', LEXICON_GROUP.QUEST_COLLECT_DEBT,
        u'Герой решает заставить должника силой после того, как не смог выполнить его задание',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION]),

        (u'QUEST_COLLECT_DEBT_DIARY_ATTACK', 380014, u'Дневник: выбор насилия', LEXICON_GROUP.QUEST_COLLECT_DEBT,
        u'Герой решает заставить должника силой',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION]),

        (u'QUEST_COLLECT_DEBT_DIARY_BEFORE_HELP', 380015, u'Дневник: выбор помощи', LEXICON_GROUP.QUEST_COLLECT_DEBT,
        u'Герой решает помочь должнику',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION]),

        (u'QUEST_COLLECT_DEBT_DIARY_FINISH_ATTACK_FAILED', 380016, u'Дневник: должник оказался сильнее', LEXICON_GROUP.QUEST_COLLECT_DEBT,
        u'Герой не смог силой заставить должника выполнить обещание.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.COINS]),

        (u'QUEST_COLLECT_DEBT_DIARY_FINISH_ATTACK_SUCCESSED_ARTIFACT', 380017, u'Дневник: награда за успешное применение насилия (артефакт)', LEXICON_GROUP.QUEST_COLLECT_DEBT,
        u'Герой получает награду за успешное применение насилия (артефакт).',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ARTIFACT]),

        (u'QUEST_COLLECT_DEBT_DIARY_FINISH_ATTACK_SUCCESSED_MONEY', 380018, u'Дневник: награда за успешное применение насилия (деньги)', LEXICON_GROUP.QUEST_COLLECT_DEBT,
        u'Герой получает награду за успешное применение насилия (деньги).',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.COINS]),

        (u'QUEST_COLLECT_DEBT_DIARY_FINISH_HELP_ARTIFACT', 380019, u'Дневник: награда за задание (артефакт)', LEXICON_GROUP.QUEST_COLLECT_DEBT,
        u'Герой получает награду за выполнение задания (артефакт).',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ARTIFACT]),

        (u'QUEST_COLLECT_DEBT_DIARY_FINISH_HELP_MONEY', 380020, u'Дневник: награда за задание (деньги)', LEXICON_GROUP.QUEST_COLLECT_DEBT,
        u'Герой получает награду за выполнение задания (деньги).',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.COINS]),

        (u'QUEST_COLLECT_DEBT_DIARY_INTRO', 380021, u'Дневник: начало задания', LEXICON_GROUP.QUEST_COLLECT_DEBT,
        u'Герой получил задание.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION]),

        (u'QUEST_COLLECT_DEBT_JOURNAL_FINISH', 380022, u'Журнал: возвращение', LEXICON_GROUP.QUEST_COLLECT_DEBT,
        u'Герой возвращается за наградой.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION]),

        (u'QUEST_COLLECT_DEBT_JOURNAL_MOVE_TO_RECEIVER', 380023, u'Журнал: начало путешествия к должнику', LEXICON_GROUP.QUEST_COLLECT_DEBT,
        u'Герой отправляется к должнику.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION]),

        (u'QUEST_COLLECT_DEBT_NAME', 380024, u'Название', LEXICON_GROUP.QUEST_COLLECT_DEBT,
        u'Краткое название задания.',
        [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION]),

        ]
