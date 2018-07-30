
import smart_imports

smart_imports.all()


V = lexicon_relations.VARIABLE


KEYS = [('QUEST_INTERFERE_ENEMY_ACTION_AFTER_INTERFERE', 500000, 'Активность: завершение', relations.LEXICON_GROUP.QUEST_INTERFERE_ENEMY,
         'Краткое суммарное описание действий героя после завершения вредительства.',
         [V.DATE, V.TIME, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION, V.HERO, V.RECEIVER], None),

        ('QUEST_INTERFERE_ENEMY_ACTION_INTRO', 500001, 'Активность: интро', relations.LEXICON_GROUP.QUEST_INTERFERE_ENEMY,
         'Краткое суммарное описание действий героя в момент получения задания.',
         [V.DATE, V.TIME, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION, V.HERO, V.RECEIVER], None),

        ('QUEST_INTERFERE_ENEMY_ACTOR_ANTAGONIST_POSITION', 500002, 'Актёр: город, где противник дела делает', relations.LEXICON_GROUP.QUEST_INTERFERE_ENEMY,
         'Название роли города, где противник дела делает.',
         [V.DATE, V.TIME, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION, V.HERO, V.RECEIVER], None),

        ('QUEST_INTERFERE_ENEMY_ACTOR_RECEIVER', 500003, 'Актёр: противник', relations.LEXICON_GROUP.QUEST_INTERFERE_ENEMY,
         'Название роли противника.',
         [V.DATE, V.TIME, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION, V.HERO, V.RECEIVER], None),

        ('QUEST_INTERFERE_ENEMY_DIARY_FINISH_ARTIFACT', 500004, 'Дневник: награда (артефакт)', relations.LEXICON_GROUP.QUEST_INTERFERE_ENEMY,
         'Герой получает награду за удачную диверсию (артефакт).',
         [V.DATE, V.TIME, V.HERO, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION, V.ARTIFACT], None),

        ('QUEST_INTERFERE_ENEMY_DIARY_FINISH_MONEY', 500005, 'Дневник: награда (деньги)', relations.LEXICON_GROUP.QUEST_INTERFERE_ENEMY,
         'Герой получает награду за удачную диверсию (деньги).',
         [V.DATE, V.TIME, V.HERO, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION, V.COINS], 'hero#N +coins#G'),

        ('QUEST_INTERFERE_ENEMY_DIARY_INTRO', 500006, 'Дневник:  начало задания', relations.LEXICON_GROUP.QUEST_INTERFERE_ENEMY,
         'Герой получил задание.',
         [V.DATE, V.TIME, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION, V.HERO, V.RECEIVER], None),

        ('QUEST_INTERFERE_ENEMY_NAME', 500007, 'Название', relations.LEXICON_GROUP.QUEST_INTERFERE_ENEMY,
         'Краткое название задания.',
         [V.DATE, V.TIME, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION, V.HERO, V.RECEIVER], None),

        ]
