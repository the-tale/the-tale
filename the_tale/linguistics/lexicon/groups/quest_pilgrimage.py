# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'QUEST_PILGRIMAGE_ACTION_INTRO', 520000, u'Активность: интро', LEXICON_GROUP.QUEST_PILGRIMAGE,
        u'Краткое суммарное описание действий героя в момент получения задания.',
        [V.RECEIVER_POSITION, V.HERO]),

        (u'QUEST_PILGRIMAGE_ACTION_SPEAK_WITH_GURU', 520001, u'Активность: разговор с гуру', LEXICON_GROUP.QUEST_PILGRIMAGE,
        u'Краткое суммарное описание действий героя во время общения с гуру.',
        [V.RECEIVER_POSITION, V.HERO]),

        (u'QUEST_PILGRIMAGE_ACTION_STAGGER_HOLY_STREETS', 520002, u'Активность: шатание по улицам', LEXICON_GROUP.QUEST_PILGRIMAGE,
        u'Краткое описание действий героя во время шатания по улицам.',
        [V.RECEIVER_POSITION, V.HERO]),

        (u'QUEST_PILGRIMAGE_ACTOR_RECEIVER_POSITION', 520003, u'Актёр: святой город', LEXICON_GROUP.QUEST_PILGRIMAGE,
        u'Название роли, святого города.',
        [V.RECEIVER_POSITION, V.HERO]),

        (u'QUEST_PILGRIMAGE_DIARY_FINISH_ARTIFACT', 520004, u'Дневник: награда (артефакт)', LEXICON_GROUP.QUEST_PILGRIMAGE,
        u'Герой получает награду за посещение города (артефакт).',
        [V.RECEIVER_POSITION, V.HERO, V.ARTIFACT]),

        (u'QUEST_PILGRIMAGE_DIARY_FINISH_MONEY', 520005, u'Дневник: награда (деньги)', LEXICON_GROUP.QUEST_PILGRIMAGE,
        u'Герой получает награду за посещение города (деньги).',
        [V.RECEIVER_POSITION, V.COINS, V.HERO]),

        (u'QUEST_PILGRIMAGE_DIARY_INTRO', 520006, u'Дневник: начало задания', LEXICON_GROUP.QUEST_PILGRIMAGE,
        u'Герой получил задание.',
        [V.RECEIVER_POSITION, V.HERO]),

        (u'QUEST_PILGRIMAGE_JOURNAL_SPEAK_WITH_GURU_DESCRIPTION', 520007, u'Описание: общение с гуру', LEXICON_GROUP.QUEST_PILGRIMAGE,
        u'Краткая декларация того, что герой общается с гуру',
        [V.HERO]),

        (u'QUEST_PILGRIMAGE_JOURNAL_SPEAK_WITH_GURU_DONOTHING', 520008, u'Журнал: общение с гуру', LEXICON_GROUP.QUEST_PILGRIMAGE,
        u'Герой общается с гуру.',
        [V.HERO]),

        (u'QUEST_PILGRIMAGE_JOURNAL_SPEAK_WITH_GURU_START', 520009, u'Журнал: начало общения с гуру', LEXICON_GROUP.QUEST_PILGRIMAGE,
        u'Герой начинает общаться с гуру.',
        [V.HERO]),

        (u'QUEST_PILGRIMAGE_JOURNAL_STAGGER_HOLY_STREETS_DESCRIPTION', 520010, u'Описание: шатание по улочкам', LEXICON_GROUP.QUEST_PILGRIMAGE,
        u'Краткая декларация того, что герой шляется по улочкам.',
        [V.HERO]),

        (u'QUEST_PILGRIMAGE_JOURNAL_STAGGER_HOLY_STREETS_DONOTHING', 520011, u'Журнал: шатание по улочкам', LEXICON_GROUP.QUEST_PILGRIMAGE,
        u'Герой шатается по улочкам',
        [V.HERO]),

        (u'QUEST_PILGRIMAGE_JOURNAL_STAGGER_HOLY_STREETS_START', 520012, u'Журнал: начало шатания по улочкам', LEXICON_GROUP.QUEST_PILGRIMAGE,
        u'Герой отправляется бродить по улочкам города.',
        [V.HERO]),

        (u'QUEST_PILGRIMAGE_NAME', 520013, u'Название', LEXICON_GROUP.QUEST_PILGRIMAGE,
        u'Краткое название задания.',
        [V.RECEIVER_POSITION, V.HERO]),

        ]
