

import smart_imports

smart_imports.all()


V = lexicon_relations.VARIABLE


KEYS = [('QUEST_PILGRIMAGE_ACTION_INTRO', 520000, 'Активность: интро', relations.LEXICON_GROUP.QUEST_PILGRIMAGE,
         'Краткое суммарное описание действий героя в момент получения задания.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO], None),

        ('QUEST_PILGRIMAGE_ACTION_SPEAK_WITH_GURU', 520001, 'Активность: разговор с гуру', relations.LEXICON_GROUP.QUEST_PILGRIMAGE,
         'Краткое суммарное описание действий героя во время общения с гуру.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO], None),

        ('QUEST_PILGRIMAGE_ACTION_STAGGER_HOLY_STREETS', 520002, 'Активность: шатание по улицам', relations.LEXICON_GROUP.QUEST_PILGRIMAGE,
         'Краткое описание действий героя во время шатания по улицам.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO], None),

        ('QUEST_PILGRIMAGE_ACTOR_RECEIVER_POSITION', 520003, 'Актёр: святой город', relations.LEXICON_GROUP.QUEST_PILGRIMAGE,
         'Название роли, святого города.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO], None),

        ('QUEST_PILGRIMAGE_DIARY_FINISH_ARTIFACT', 520004, 'Дневник: награда (артефакт)', relations.LEXICON_GROUP.QUEST_PILGRIMAGE,
         'Герой получает награду за посещение города (артефакт).',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO, V.ARTIFACT], None),

        ('QUEST_PILGRIMAGE_DIARY_FINISH_MONEY', 520005, 'Дневник: награда (деньги)', relations.LEXICON_GROUP.QUEST_PILGRIMAGE,
         'Герой получает награду за посещение города (деньги).',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.COINS, V.HERO], 'hero#N +coins#G'),

        ('QUEST_PILGRIMAGE_DIARY_INTRO', 520006, 'Дневник: начало задания', relations.LEXICON_GROUP.QUEST_PILGRIMAGE,
         'Герой получил задание.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO], None),

        ('QUEST_PILGRIMAGE_JOURNAL_SPEAK_WITH_GURU_DESCRIPTION', 520007, 'Описание: общение с гуру', relations.LEXICON_GROUP.QUEST_PILGRIMAGE,
         'Краткая декларация того, что герой общается с гуру',
         [V.DATE, V.TIME, V.HERO], None),

        ('QUEST_PILGRIMAGE_JOURNAL_SPEAK_WITH_GURU_DONOTHING', 520008, 'Журнал: общение с гуру', relations.LEXICON_GROUP.QUEST_PILGRIMAGE,
         'Герой общается с гуру.',
         [V.DATE, V.TIME, V.HERO], None),

        ('QUEST_PILGRIMAGE_JOURNAL_SPEAK_WITH_GURU_START', 520009, 'Журнал: начало общения с гуру', relations.LEXICON_GROUP.QUEST_PILGRIMAGE,
         'Герой начинает общаться с гуру.',
         [V.DATE, V.TIME, V.HERO], None),

        ('QUEST_PILGRIMAGE_JOURNAL_STAGGER_HOLY_STREETS_DESCRIPTION', 520010, 'Описание: шатание по улочкам', relations.LEXICON_GROUP.QUEST_PILGRIMAGE,
         'Краткая декларация того, что герой шляется по улочкам.',
         [V.DATE, V.TIME, V.HERO], None),

        ('QUEST_PILGRIMAGE_JOURNAL_STAGGER_HOLY_STREETS_DONOTHING', 520011, 'Журнал: шатание по улочкам', relations.LEXICON_GROUP.QUEST_PILGRIMAGE,
         'Герой шатается по улочкам',
         [V.DATE, V.TIME, V.HERO], None),

        ('QUEST_PILGRIMAGE_JOURNAL_STAGGER_HOLY_STREETS_START', 520012, 'Журнал: начало шатания по улочкам', relations.LEXICON_GROUP.QUEST_PILGRIMAGE,
         'Герой отправляется бродить по улочкам города.',
         [V.DATE, V.TIME, V.HERO], None),

        ('QUEST_PILGRIMAGE_NAME', 520013, 'Название', relations.LEXICON_GROUP.QUEST_PILGRIMAGE,
         'Краткое название задания.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO], None),

        ]
