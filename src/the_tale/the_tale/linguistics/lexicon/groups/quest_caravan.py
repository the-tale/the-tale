# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [('QUEST_CARAVAN_ACTION_ATTACK', 360000, 'Активность: нападение на охрану', LEXICON_GROUP.QUEST_CARAVAN,
        'Краткое суммарное описание действий героя, когда он сражается с охраной',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_ACTION_CHOOSE_ATTACK', 360001, 'Активность: выбор ограбления', LEXICON_GROUP.QUEST_CARAVAN,
        'Краткое суммарное описание действий героя при выборе ограбления каравана',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_ACTION_CHOOSE_DEFENCE', 360002, 'Активность: выбор защиты от бандитов', LEXICON_GROUP.QUEST_CARAVAN,
        'Краткое суммарное описание действий героя при выборе защиты каравана от бандитов',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_ACTION_DEFENCE', 360003, 'Активность: атака бандитов', LEXICON_GROUP.QUEST_CARAVAN,
        'Краткое суммарное описание действий героя при атаке бандитов.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_ACTION_FIGHT', 360004, 'Активность: отбивается от преследователей', LEXICON_GROUP.QUEST_CARAVAN,
        'Краткое суммарное описание действий героя, когда он отбивается от преследователей.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_ACTION_FINISH_ATTACK', 360005, 'Активность: продажа добычи', LEXICON_GROUP.QUEST_CARAVAN,
        'Краткое суммарное описание действий героя, когда он продаёт добычу.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_ACTION_FINISH_DEFENCE', 360006, 'Активность: успешное отражение атаки бандитов', LEXICON_GROUP.QUEST_CARAVAN,
        'Краткое суммарное описание действий героя после успешного отражения атаки бандитов.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_ACTION_FIRST_MOVING', 360007, 'Активность: сопровождение каравана', LEXICON_GROUP.QUEST_CARAVAN,
        'Краткое суммарное описание действий героя при сопровождении каравана',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_ACTION_HIDE', 360008, 'Активность: идти на чёрный рынок', LEXICON_GROUP.QUEST_CARAVAN,
        'Краткое суммарное описание действий героя, когда он идёт на чёрный рынок.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_ACTION_INTRO', 360009, 'Активность: интро', LEXICON_GROUP.QUEST_CARAVAN,
        'Краткое суммарное описание действий героя в момент получения задания.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_ACTION_START_HIDE', 360010, 'Активность: скрыться с награбленным', LEXICON_GROUP.QUEST_CARAVAN,
        'Краткое суммарное описание действий героя, когда он прячется и путает следы.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_ACTION_START_RUN', 360011, 'Активность: убегание с добычей', LEXICON_GROUP.QUEST_CARAVAN,
        'Краткое суммарное описание действий героя, когда он убегает с добычей',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_ACTOR_ANTAGONIST_POSITION', 360012, 'Актёр: чёрный рынок', LEXICON_GROUP.QUEST_CARAVAN,
        'Название роли, чёрного рынка.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_ACTOR_INITIATOR', 360013, 'Актёр: инициатор задания', LEXICON_GROUP.QUEST_CARAVAN,
        'Название роли, инициирующей задание.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_ACTOR_RECEIVER', 360014, 'Актёр: ожидающий караван', LEXICON_GROUP.QUEST_CARAVAN,
        'Название роли, ожидающего прибыитие каравана.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_CHOICE_CURRENT_JUMP_ATTACK', 360015, 'Выбор: ограбление', LEXICON_GROUP.QUEST_CARAVAN,
        'Краткая констатация выбора героя в случае ограбления каравана.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_CHOICE_CURRENT_JUMP_DEFENCE', 360016, 'Выбор: защита', LEXICON_GROUP.QUEST_CARAVAN,
        'Краткая констатация выбора героя в случае защиты каравана.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_CHOICE_VARIANT_JUMP_ATTACK', 360017, 'Вариант выбора: ограбление', LEXICON_GROUP.QUEST_CARAVAN,
        'Краткое описание варианта выбора, ведущего к ограблению каравана.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_CHOICE_VARIANT_JUMP_DEFENCE', 360018, 'Вариант выбора: защита', LEXICON_GROUP.QUEST_CARAVAN,
        'Краткое описание варианта выбора, ведущего к защите каравана.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_DIARY_CHOOSE_ATTACK', 360019, 'Дневник: выбор ограбления', LEXICON_GROUP.QUEST_CARAVAN,
        'Герой решил ограбить караван.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_DIARY_CHOOSE_DEFENCE', 360020, 'Дневник: выбор защиты', LEXICON_GROUP.QUEST_CARAVAN,
        'Герой решил защищать караван.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_DIARY_FINISH_ATTACK_ARTIFACT', 360021, 'Дневник: награда за ограбление (артефакт)', LEXICON_GROUP.QUEST_CARAVAN,
        'Герой получает награду за ограбление каравана. (артефакт)',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION, V.ARTIFACT], None),

        ('QUEST_CARAVAN_DIARY_FINISH_ATTACK_FAILED', 360022, 'Дневник: герой не смог ограбить караван', LEXICON_GROUP.QUEST_CARAVAN,
        'Герой не смог ограбить караван.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_DIARY_FINISH_ATTACK_MONEY', 360023, 'Дневник: награда за ограбление (деньги)', LEXICON_GROUP.QUEST_CARAVAN,
        'Герой получает награду за ограбление каравана (деньги).',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION, V.COINS], 'hero#N +coins#G'),

        ('QUEST_CARAVAN_DIARY_FINISH_DEFENCE_ARTIFACT', 360024, 'Дневник: награда за защиту (артефакт)', LEXICON_GROUP.QUEST_CARAVAN,
        'Герой получает награду за защиту каравана (артефакт).',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION, V.ARTIFACT], None),

        ('QUEST_CARAVAN_DIARY_FINISH_DEFENCE_FAILED', 360025, 'Дневник: герой не смог защитить караван', LEXICON_GROUP.QUEST_CARAVAN,
        'Герой не смог защитить караван.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_DIARY_FINISH_DEFENCE_MONEY', 360026, 'Дневник: награда за защиту (деньги)', LEXICON_GROUP.QUEST_CARAVAN,
        'Герой получает награду за защиту каравана (деньги).',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION, V.COINS], 'hero#N +coins#G'),

        ('QUEST_CARAVAN_DIARY_INTRO', 360027, 'Дневник: начало задания', LEXICON_GROUP.QUEST_CARAVAN,
        'Герой получил задание.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_JOURNAL_ATTACK', 360028, 'Журнал: атака героя', LEXICON_GROUP.QUEST_CARAVAN,
        'Начало атаки героя на караван.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_JOURNAL_DEFENCE', 360029, 'Журнал: атака бандитов', LEXICON_GROUP.QUEST_CARAVAN,
        'Начало атаки бандитов на караван.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_JOURNAL_FIGHT', 360030, 'Журнал: герой отбивается от преследователей', LEXICON_GROUP.QUEST_CARAVAN,
        '.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_JOURNAL_HIDE', 360031, 'Журнал: герой убирается восвояси', LEXICON_GROUP.QUEST_CARAVAN,
        '.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_JOURNAL_STURT_RUN', 360032, 'Журнал: герой убегает с добычей', LEXICON_GROUP.QUEST_CARAVAN,
        '.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ('QUEST_CARAVAN_NAME', 360033, 'Название', LEXICON_GROUP.QUEST_CARAVAN,
        'Краткое название задания.',
        [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.ANTAGONIST_POSITION, V.RECEIVER_POSITION], None),

        ]
