# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'QUEST_HUNT_ACTION_FIGHT', 480000, u'Активность: охота', LEXICON_GROUP.QUEST_HUNT,
        u'Краткое суммарное описание действий героя во время преследования добычи.',
        [V.RECEIVER_POSITION, V.HERO]),

        (u'QUEST_HUNT_ACTION_INTRO', 480001, u'Активность: интро', LEXICON_GROUP.QUEST_HUNT,
        u'Краткое суммарное описание действий героя в момент получения задания.',
        [V.RECEIVER_POSITION, V.HERO]),

        (u'QUEST_HUNT_ACTION_MOVE_TO_HUNT', 480002, u'Активность: путешествие к месту охоты', LEXICON_GROUP.QUEST_HUNT,
        u'Краткое суммарное описание действий героя во время путешествия к месту охоты.',
        [V.RECEIVER_POSITION, V.HERO]),

        (u'QUEST_HUNT_ACTION_RETURN_WITH_PREY', 480003, u'Активность: возвращение с добычей', LEXICON_GROUP.QUEST_HUNT,
        u'Краткое суммарное описание действий героя во время возвращения с добычей.',
        [V.RECEIVER_POSITION, V.HERO]),

        (u'QUEST_HUNT_ACTION_START_TRACK', 480004, u'Активность: выслеживание добычи', LEXICON_GROUP.QUEST_HUNT,
        u'Краткое суммарное описание действий героя во время выслеживания добычи.',
        [V.RECEIVER_POSITION, V.HERO]),

        (u'QUEST_HUNT_ACTOR_RECEIVER_POSITION', 480005, u'Актёр: место охоты', LEXICON_GROUP.QUEST_HUNT,
        u'Название роли, места охоты.',
        [V.RECEIVER_POSITION, V.HERO]),

        (u'QUEST_HUNT_DIARY_INTRO', 480006, u'Дневник: начало задания', LEXICON_GROUP.QUEST_HUNT,
        u'Герой получил задание.',
        [V.RECEIVER_POSITION, V.HERO]),

        (u'QUEST_HUNT_DIARY_SELL_PREY_ARTIFACT', 480007, u'Дневник: награда (артефакт)', LEXICON_GROUP.QUEST_HUNT,
        u'Герой получил награду за выполнение задания (артефакт)',
        [V.RECEIVER_POSITION, V.HERO, V.ARTIFACT]),

        (u'QUEST_HUNT_DIARY_SELL_PREY_MONEY', 480008, u'Дневник: награда (деньги)', LEXICON_GROUP.QUEST_HUNT,
        u'Герой получил награду за выполнение задания (деньги)',
        [V.RECEIVER_POSITION, V.COINS, V.HERO]),

        (u'QUEST_HUNT_JOURNAL_MOVE_TO_HUNT', 480009, u'Журнал: отправление в места охоты', LEXICON_GROUP.QUEST_HUNT,
        u'Герой отправляется в места обитания дичи.',
        [V.RECEIVER_POSITION, V.HERO]),

        (u'QUEST_HUNT_JOURNAL_RETURN_WITH_PREY', 480010, u'Журнал: возвращение с добычей', LEXICON_GROUP.QUEST_HUNT,
        u'Герой отправляется в обратную дорогу, нагруженный добычей',
        [V.RECEIVER_POSITION, V.HERO]),

        (u'QUEST_HUNT_JOURNAL_START_TRACK', 480011, u'Журнал: выслеживание добычи', LEXICON_GROUP.QUEST_HUNT,
        u'Герой нашёл следы дичи.',
        [V.RECEIVER_POSITION, V.HERO]),

        (u'QUEST_HUNT_NAME', 480012, u'Название', LEXICON_GROUP.QUEST_HUNT,
        u'Краткое название задания.',
        [V.RECEIVER_POSITION, V.HERO]),

        ]
