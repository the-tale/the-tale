# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'QUEST_HELP_FRIEND_ACTION_AFTER_HELP', 440000, u'Активность: после выполнения задания на помощь', LEXICON_GROUP.QUEST_HELP_FRIEND,
        u'Краткое суммарное описание действий героя после выполнения взятием задания.',
        [V.RECEIVER_POSITION, V.HERO, V.RECEIVER]),

        (u'QUEST_HELP_FRIEND_ACTION_BEFORE_HELP', 440001, u'Активность: перед взятием задания на помощь', LEXICON_GROUP.QUEST_HELP_FRIEND,
        u'Краткое суммарное описание действий героя перед взятием задания на помощь.',
        [V.RECEIVER_POSITION, V.HERO, V.RECEIVER]),

        (u'QUEST_HELP_FRIEND_ACTION_INTRO', 440002, u'Активность: интро', LEXICON_GROUP.QUEST_HELP_FRIEND,
        u'Краткое суммарное описание действий героя в момент получения задания.',
        [V.RECEIVER_POSITION, V.HERO, V.RECEIVER]),

        (u'QUEST_HELP_FRIEND_ACTOR_RECEIVER', 440003, u'Актёр: Соратник', LEXICON_GROUP.QUEST_HELP_FRIEND,
        u'Название роли, соратника.',
        [V.RECEIVER_POSITION, V.HERO, V.RECEIVER]),

        (u'QUEST_HELP_FRIEND_DIARY_FINISH_MEETING_ARTIFACT', 440004, u'Дневник: награда за удавшуюся помощь (артефакт)', LEXICON_GROUP.QUEST_HELP_FRIEND,
        u'Герой получает награду за удавшуюся попытку помочь (артефакт).',
        [V.RECEIVER_POSITION, V.HERO, V.ARTIFACT, V.RECEIVER]),

        (u'QUEST_HELP_FRIEND_DIARY_FINISH_MEETING_MONEY', 440005, u'Дневник: награда за удавшуюся помощь (деньги)', LEXICON_GROUP.QUEST_HELP_FRIEND,
        u'Герой получает награду за удавшуюся попытку помочь (деньги).',
        [V.RECEIVER_POSITION, V.COINS, V.HERO, V.RECEIVER]),

        (u'QUEST_HELP_FRIEND_DIARY_INTRO', 440006, u'Дневник: начало задания', LEXICON_GROUP.QUEST_HELP_FRIEND,
        u'Герой получил задание.',
        [V.RECEIVER_POSITION, V.HERO, V.RECEIVER]),

        (u'QUEST_HELP_FRIEND_NAME', 440007, u'Название', LEXICON_GROUP.QUEST_HELP_FRIEND,
        u'Краткое название задания.',
        [V.RECEIVER_POSITION, V.HERO, V.RECEIVER]),

        ]
