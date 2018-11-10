

import smart_imports

smart_imports.all()


V = lexicon_relations.VARIABLE


KEYS = [('QUEST_HELP_FRIEND_ACTION_AFTER_HELP', 440000, 'Активность: после выполнения задания на помощь', relations.LEXICON_GROUP.QUEST_HELP_FRIEND,
         'Краткое суммарное описание действий героя после выполнения взятого задания.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO, V.RECEIVER], None),

        ('QUEST_HELP_FRIEND_ACTION_BEFORE_HELP', 440001, 'Активность: перед взятием задания на помощь', relations.LEXICON_GROUP.QUEST_HELP_FRIEND,
         'Краткое суммарное описание действий героя перед взятием задания на помощь.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO, V.RECEIVER], None),

        ('QUEST_HELP_FRIEND_ACTION_INTRO', 440002, 'Активность: интро', relations.LEXICON_GROUP.QUEST_HELP_FRIEND,
         'Краткое суммарное описание действий героя в момент получения задания.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO, V.RECEIVER], None),

        ('QUEST_HELP_FRIEND_ACTOR_RECEIVER', 440003, 'Актёр: Соратник', relations.LEXICON_GROUP.QUEST_HELP_FRIEND,
         'Название роли, соратника.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO, V.RECEIVER], None),

        ('QUEST_HELP_FRIEND_DIARY_FINISH_MEETING_ARTIFACT', 440004, 'Дневник: награда за удавшуюся помощь (артефакт)', relations.LEXICON_GROUP.QUEST_HELP_FRIEND,
         'Герой получает награду за удавшуюся попытку помочь (артефакт).',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO, V.ARTIFACT, V.RECEIVER], None),

        ('QUEST_HELP_FRIEND_DIARY_FINISH_MEETING_MONEY', 440005, 'Дневник: награда за удавшуюся помощь (деньги)', relations.LEXICON_GROUP.QUEST_HELP_FRIEND,
         'Герой получает награду за удавшуюся попытку помочь (деньги).',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.COINS, V.HERO, V.RECEIVER], 'hero#N +coins#G'),

        ('QUEST_HELP_FRIEND_DIARY_INTRO', 440006, 'Дневник: начало задания', relations.LEXICON_GROUP.QUEST_HELP_FRIEND,
         'Герой получил задание.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO, V.RECEIVER], None),

        ('QUEST_HELP_FRIEND_NAME', 440007, 'Название', relations.LEXICON_GROUP.QUEST_HELP_FRIEND,
         'Краткое название задания.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO, V.RECEIVER], None),

        ]
