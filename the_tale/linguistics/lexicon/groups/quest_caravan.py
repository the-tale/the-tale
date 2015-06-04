# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'QUEST_CARAVAN_ACTION_ATTACK', 360000, u'Активность: нападение на охрану', LEXICON_GROUP.QUEST_CARAVAN,
        u'Краткое суммарное описание действий героя, когда он сражается с охраной',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_ACTION_CHOOSE_ATTACK', 360001, u'Активность: выбор ограбления', LEXICON_GROUP.QUEST_CARAVAN,
        u'Краткое суммарное описание действий героя при выборе ограбления каравана',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_ACTION_CHOOSE_DEFENCE', 360002, u'Активность: выбор защиты от бандитов', LEXICON_GROUP.QUEST_CARAVAN,
        u'Краткое суммарное описание действий героя при выборе защиты каравана от бандитов',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_ACTION_DEFENCE', 360003, u'Активность: атака бандитов', LEXICON_GROUP.QUEST_CARAVAN,
        u'Краткое суммарное описание действий героя при атаке бандитов.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_ACTION_FIGHT', 360004, u'Активность: отбивается от преследователей', LEXICON_GROUP.QUEST_CARAVAN,
        u'Краткое суммарное описание действий героя, когда он отбивается от преследователей.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_ACTION_FINISH_ATTACK', 360005, u'Активность: продажа добычи', LEXICON_GROUP.QUEST_CARAVAN,
        u'Краткое суммарное описание действий героя, когда он продаёт добычу.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_ACTION_FINISH_DEFENCE', 360006, u'Активность: успешное отражение атаки бандитов', LEXICON_GROUP.QUEST_CARAVAN,
        u'Краткое суммарное описание действий героя после успешного отражения атаки бандитов.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_ACTION_FIRST_MOVING', 360007, u'Активность: сопровождение каравана', LEXICON_GROUP.QUEST_CARAVAN,
        u'Краткое суммарное описание действий героя при сопровождении каравана',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_ACTION_HIDE', 360008, u'Активность: идти на чёрный рынок', LEXICON_GROUP.QUEST_CARAVAN,
        u'Краткое суммарное описание действий героя, когда он идёт на чёрный рынок.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_ACTION_INTRO', 360009, u'Активность: интро', LEXICON_GROUP.QUEST_CARAVAN,
        u'Краткое суммарное описание действий героя в момент получения задания.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_ACTION_START_HIDE', 360010, u'Активность: скрыться с награбленным', LEXICON_GROUP.QUEST_CARAVAN,
        u'Краткое суммарное описание действий героя, когда он прячется и путает следы.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_ACTION_START_RUN', 360011, u'Активность: убегание с добычей', LEXICON_GROUP.QUEST_CARAVAN,
        u'Краткое суммарное описание действий героя, когда он убегает с добычей',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_ACTOR_ANTAGONIST_POSITION', 360012, u'Актёр: чёрный рынок', LEXICON_GROUP.QUEST_CARAVAN,
        u'Название роли, чёрного рынка.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_ACTOR_INITIATOR', 360013, u'Актёр: инициатор задания', LEXICON_GROUP.QUEST_CARAVAN,
        u'Название роли, инициирующей задание.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_ACTOR_RECEIVER', 360014, u'Актёр: ожидающий караван', LEXICON_GROUP.QUEST_CARAVAN,
        u'Название роли, ожидающего прибыитие каравана.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_CHOICE_CURRENT_JUMP_ATTACK', 360015, u'Выбор: ограбление', LEXICON_GROUP.QUEST_CARAVAN,
        u'Краткая констатация выбора героя в случае ограбления каравана.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_CHOICE_CURRENT_JUMP_DEFENCE', 360016, u'Выбор: защита', LEXICON_GROUP.QUEST_CARAVAN,
        u'Краткая констатация выбора героя в случае защиты каравана.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_CHOICE_VARIANT_JUMP_ATTACK', 360017, u'Вариант выбора: ограбление', LEXICON_GROUP.QUEST_CARAVAN,
        u'Краткое описание варианта выбора, ведущего к ограблению каравана.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_CHOICE_VARIANT_JUMP_DEFENCE', 360018, u'Вариант выбора: защита', LEXICON_GROUP.QUEST_CARAVAN,
        u'Краткое описание варианта выбора, ведущего к защите каравана.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_DIARY_CHOOSE_ATTACK', 360019, u'Дневник: выбор ограбления', LEXICON_GROUP.QUEST_CARAVAN,
        u'Герой решил ограбить караван.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_DIARY_CHOOSE_DEFENCE', 360020, u'Дневник: выбор защиты', LEXICON_GROUP.QUEST_CARAVAN,
        u'Герой решил защищать караван.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_DIARY_FINISH_ATTACK_ARTIFACT', 360021, u'Дневник: награда за ограбление (артефакт)', LEXICON_GROUP.QUEST_CARAVAN,
        u'Герой получает награду за ограбление каравана. (артефакт)',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION, V.ARTIFACT]),

        (u'QUEST_CARAVAN_DIARY_FINISH_ATTACK_FAILED', 360022, u'Дневник: герой не смог ограбить караван', LEXICON_GROUP.QUEST_CARAVAN,
        u'Герой не смог ограбить караван.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_DIARY_FINISH_ATTACK_MONEY', 360023, u'Дневник: награда за ограбление (деньги)', LEXICON_GROUP.QUEST_CARAVAN,
        u'Герой получает награду за ограбление каравана (деньги).',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION, V.COINS]),

        (u'QUEST_CARAVAN_DIARY_FINISH_DEFENCE_ARTIFACT', 360024, u'Дневник: награда за защиту (артефакт)', LEXICON_GROUP.QUEST_CARAVAN,
        u'Герой получает награду за защиту каравана (артефакт).',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION, V.ARTIFACT]),

        (u'QUEST_CARAVAN_DIARY_FINISH_DEFENCE_FAILED', 360025, u'Дневник: герой не смог защитить караван', LEXICON_GROUP.QUEST_CARAVAN,
        u'Герой не смог защитить караван.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_DIARY_FINISH_DEFENCE_MONEY', 360026, u'Дневник: награда за защиту (деньги)', LEXICON_GROUP.QUEST_CARAVAN,
        u'Герой получает награду за защиту каравана (деньги).',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION, V.COINS]),

        (u'QUEST_CARAVAN_DIARY_INTRO', 360027, u'Дневник: начало задания', LEXICON_GROUP.QUEST_CARAVAN,
        u'Герой получил задание.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_JOURNAL_ATTACK', 360028, u'Журнал: атака героя', LEXICON_GROUP.QUEST_CARAVAN,
        u'Начало атаки героя на караван.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_JOURNAL_DEFENCE', 360029, u'Журнал: атака бандитов', LEXICON_GROUP.QUEST_CARAVAN,
        u'Начало атаки бандитов на караван.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_JOURNAL_FIGHT', 360030, u'Журнал: герой отбивается от преследователей', LEXICON_GROUP.QUEST_CARAVAN,
        u'.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_JOURNAL_HIDE', 360031, u'Журнал: герой убирается восвояси', LEXICON_GROUP.QUEST_CARAVAN,
        u'.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_JOURNAL_STURT_RUN', 360032, u'Журнал: герой убегает с добычей', LEXICON_GROUP.QUEST_CARAVAN,
        u'.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        (u'QUEST_CARAVAN_NAME', 360033, u'Название', LEXICON_GROUP.QUEST_CARAVAN,
        u'Краткое название задания.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION]),

        ]
