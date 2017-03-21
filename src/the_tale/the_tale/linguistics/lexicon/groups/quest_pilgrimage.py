# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [('QUEST_PILGRIMAGE_ACTION_INTRO', 520000, 'Активность: интро', LEXICON_GROUP.QUEST_PILGRIMAGE,
        'Краткое суммарное описание действий героя в момент получения задания.',
        [V.DATE, V.RECEIVER_POSITION, V.HERO], None),

        ('QUEST_PILGRIMAGE_ACTION_SPEAK_WITH_GURU', 520001, 'Активность: разговор с гуру', LEXICON_GROUP.QUEST_PILGRIMAGE,
        'Краткое суммарное описание действий героя во время общения с гуру.',
        [V.DATE, V.RECEIVER_POSITION, V.HERO], None),

        ('QUEST_PILGRIMAGE_ACTION_STAGGER_HOLY_STREETS', 520002, 'Активность: шатание по улицам', LEXICON_GROUP.QUEST_PILGRIMAGE,
        'Краткое описание действий героя во время шатания по улицам.',
        [V.DATE, V.RECEIVER_POSITION, V.HERO], None),

        ('QUEST_PILGRIMAGE_ACTOR_RECEIVER_POSITION', 520003, 'Актёр: святой город', LEXICON_GROUP.QUEST_PILGRIMAGE,
        'Название роли, святого города.',
        [V.DATE, V.RECEIVER_POSITION, V.HERO], None),

        ('QUEST_PILGRIMAGE_DIARY_FINISH_ARTIFACT', 520004, 'Дневник: награда (артефакт)', LEXICON_GROUP.QUEST_PILGRIMAGE,
        'Герой получает награду за посещение города (артефакт).',
        [V.DATE, V.RECEIVER_POSITION, V.HERO, V.ARTIFACT], None),

        ('QUEST_PILGRIMAGE_DIARY_FINISH_MONEY', 520005, 'Дневник: награда (деньги)', LEXICON_GROUP.QUEST_PILGRIMAGE,
        'Герой получает награду за посещение города (деньги).',
        [V.DATE, V.RECEIVER_POSITION, V.COINS, V.HERO], 'hero#N +coins#G'),

        ('QUEST_PILGRIMAGE_DIARY_INTRO', 520006, 'Дневник: начало задания', LEXICON_GROUP.QUEST_PILGRIMAGE,
        'Герой получил задание.',
        [V.DATE, V.RECEIVER_POSITION, V.HERO], None),

        ('QUEST_PILGRIMAGE_JOURNAL_SPEAK_WITH_GURU_DESCRIPTION', 520007, 'Описание: общение с гуру', LEXICON_GROUP.QUEST_PILGRIMAGE,
        'Краткая декларация того, что герой общается с гуру',
        [V.DATE, V.HERO], None),

        ('QUEST_PILGRIMAGE_JOURNAL_SPEAK_WITH_GURU_DONOTHING', 520008, 'Журнал: общение с гуру', LEXICON_GROUP.QUEST_PILGRIMAGE,
        'Герой общается с гуру.',
        [V.DATE, V.HERO], None),

        ('QUEST_PILGRIMAGE_JOURNAL_SPEAK_WITH_GURU_START', 520009, 'Журнал: начало общения с гуру', LEXICON_GROUP.QUEST_PILGRIMAGE,
        'Герой начинает общаться с гуру.',
        [V.DATE, V.HERO], None),

        ('QUEST_PILGRIMAGE_JOURNAL_STAGGER_HOLY_STREETS_DESCRIPTION', 520010, 'Описание: шатание по улочкам', LEXICON_GROUP.QUEST_PILGRIMAGE,
        'Краткая декларация того, что герой шляется по улочкам.',
        [V.DATE, V.HERO], None),

        ('QUEST_PILGRIMAGE_JOURNAL_STAGGER_HOLY_STREETS_DONOTHING', 520011, 'Журнал: шатание по улочкам', LEXICON_GROUP.QUEST_PILGRIMAGE,
        'Герой шатается по улочкам',
        [V.DATE, V.HERO], None),

        ('QUEST_PILGRIMAGE_JOURNAL_STAGGER_HOLY_STREETS_START', 520012, 'Журнал: начало шатания по улочкам', LEXICON_GROUP.QUEST_PILGRIMAGE,
        'Герой отправляется бродить по улочкам города.',
        [V.DATE, V.HERO], None),

        ('QUEST_PILGRIMAGE_NAME', 520013, 'Название', LEXICON_GROUP.QUEST_PILGRIMAGE,
        'Краткое название задания.',
        [V.DATE, V.RECEIVER_POSITION, V.HERO], None),

        ]
