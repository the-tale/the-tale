# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'QUEST_INTERFERE_ENEMY_ACTION_AFTER_INTERFERE', 500000, u'Активность: завершение', LEXICON_GROUP.QUEST_INTERFERE_ENEMY,
        u'Краткое суммарное описание действий героя после завершения вредительства.',
        [V.ANTAGONIST_POSITION, V.RECEIVER_POSITION, V.HERO, V.RECEIVER]),

        (u'QUEST_INTERFERE_ENEMY_ACTION_INTRO', 500001, u'Активность: интро', LEXICON_GROUP.QUEST_INTERFERE_ENEMY,
        u'Краткое суммарное описание действий героя в момент получения задания.',
        [V.ANTAGONIST_POSITION, V.RECEIVER_POSITION, V.HERO, V.RECEIVER]),

        (u'QUEST_INTERFERE_ENEMY_ACTOR_ANTAGONIST_POSITION', 500002, u'Актёр: город, где противник дела делает', LEXICON_GROUP.QUEST_INTERFERE_ENEMY,
        u'Название роли города, где противник дела делает.',
        [V.ANTAGONIST_POSITION, V.RECEIVER_POSITION, V.HERO, V.RECEIVER]),

        (u'QUEST_INTERFERE_ENEMY_ACTOR_RECEIVER', 500003, u'Актёр: противник', LEXICON_GROUP.QUEST_INTERFERE_ENEMY,
        u'Название роли противника.',
        [V.ANTAGONIST_POSITION, V.RECEIVER_POSITION, V.HERO, V.RECEIVER]),

        (u'QUEST_INTERFERE_ENEMY_DIARY_FINISH_ARTIFACT', 500004, u'Дневник: награда (артефакт)', LEXICON_GROUP.QUEST_INTERFERE_ENEMY,
        u'Герой получает награду за удачную диверсию (артефакт).',
        [V.HERO, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION, V.ARTIFACT]),

        (u'QUEST_INTERFERE_ENEMY_DIARY_FINISH_MONEY', 500005, u'Дневник: награда (деньги)', LEXICON_GROUP.QUEST_INTERFERE_ENEMY,
        u'Герой получает награду за удачную диверсию (деньги).',
        [V.HERO, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION, V.COINS]),

        (u'QUEST_INTERFERE_ENEMY_DIARY_INTRO', 500006, u'Дневник:  начало задания', LEXICON_GROUP.QUEST_INTERFERE_ENEMY,
        u'Герой получил задание.',
        [V.ANTAGONIST_POSITION, V.RECEIVER_POSITION, V.HERO, V.RECEIVER]),

        (u'QUEST_INTERFERE_ENEMY_NAME', 500007, u'Название', LEXICON_GROUP.QUEST_INTERFERE_ENEMY,
        u'Краткое название задания.',
        [V.ANTAGONIST_POSITION, V.RECEIVER_POSITION, V.HERO, V.RECEIVER]),

        ]
