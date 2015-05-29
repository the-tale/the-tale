# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'QUEST_HOMETOWN_ACTION_CHATTING', 460000, u'Активность: общение с друзьями', LEXICON_GROUP.QUEST_HOMETOWN,
        u'Краткое суммарное описание действий героя во время общения с друзьями.',
        [V.HERO]),

        (u'QUEST_HOMETOWN_ACTION_DRUNK_SONG', 460001, u'Активность: пьяная песня', LEXICON_GROUP.QUEST_HOMETOWN,
        u'Краткое суммарное описание действий героя во время пения пьяных песен.',
        [V.HERO]),

        (u'QUEST_HOMETOWN_ACTION_INTRO', 460002, u'Активность: интро', LEXICON_GROUP.QUEST_HOMETOWN,
        u'Краткое суммарное описание действий героя в момент получения задания.',
        [V.RECEIVER_POSITION, V.HERO]),

        (u'QUEST_HOMETOWN_ACTION_REMEMBER_NAMES', 460003, u'Активность: вспоминание имён', LEXICON_GROUP.QUEST_HOMETOWN,
        u'Краткое описание действий героя во время вспоминания имён жителей города',
        [V.HERO]),

        (u'QUEST_HOMETOWN_ACTION_SEARCH_OLD_FRIENDS', 460004, u'Активность: поиск старых знакомых', LEXICON_GROUP.QUEST_HOMETOWN,
        u'Краткое суммарное описание действий героя во время поиска старых друзей.',
        [V.HERO]),

        (u'QUEST_HOMETOWN_ACTION_STAGGER_STREETS', 460005, u'Активность: шатание по улицам', LEXICON_GROUP.QUEST_HOMETOWN,
        u'Краткое описание действий героя во время шатания по улицам.',
        [V.HERO]),

        (u'QUEST_HOMETOWN_ACTOR_RECEIVER_POSITION', 460006, u'Актёр: родной город', LEXICON_GROUP.QUEST_HOMETOWN,
        u'Название роли, родной город.',
        [V.RECEIVER_POSITION, V.HERO]),

        (u'QUEST_HOMETOWN_DIARY_FINISH_ARTIFACT', 460007, u'Дневник: награда (артефакт)', LEXICON_GROUP.QUEST_HOMETOWN,
        u'Герой получает награду за посещение города (артефакт).',
        [V.RECEIVER_POSITION, V.HERO, V.ARTIFACT]),

        (u'QUEST_HOMETOWN_DIARY_FINISH_MONEY', 460008, u'Дневник: награда (деньги)', LEXICON_GROUP.QUEST_HOMETOWN,
        u'Герой получает награду за посещение города (деньги).',
        [V.RECEIVER_POSITION, V.COINS, V.HERO]),

        (u'QUEST_HOMETOWN_DIARY_INTRO', 460009, u'Дневник: начало задания', LEXICON_GROUP.QUEST_HOMETOWN,
        u'Герой получил задание.',
        [V.RECEIVER_POSITION, V.HERO]),

        (u'QUEST_HOMETOWN_JOURNAL_CHATTING_DESCRIPTION', 460010, u'Описание: общение с друзьями', LEXICON_GROUP.QUEST_HOMETOWN,
        u'Краткая декларация того, что герой болтает с друзьями.',
        [V.HERO]),

        (u'QUEST_HOMETOWN_JOURNAL_CHATTING_DONOTHING', 460011, u'Журнал: фразы во время болтания с друзьями', LEXICON_GROUP.QUEST_HOMETOWN,
        u'Фразы, которые герой говорит, болтая с друзьями',
        [V.HERO]),

        (u'QUEST_HOMETOWN_JOURNAL_CHATTING_START', 460012, u'Журнал: начало разговора с друзьями', LEXICON_GROUP.QUEST_HOMETOWN,
        u'Герой начинает болтать с друзьями.',
        [V.HERO]),

        (u'QUEST_HOMETOWN_JOURNAL_DRUNK_SONG_DESCRIPTION', 460013, u'Описание: начало пьяной песни', LEXICON_GROUP.QUEST_HOMETOWN,
        u'Краткая декларация того, что герой поёт пьяную песню',
        [V.HERO]),

        (u'QUEST_HOMETOWN_JOURNAL_DRUNK_SONG_DONOTHING', 460014, u'Журнал: пьяное пение', LEXICON_GROUP.QUEST_HOMETOWN,
        u'Герой поёт пьяную песню.',
        [V.HERO]),

        (u'QUEST_HOMETOWN_JOURNAL_DRUNK_SONG_START', 460015, u'Журнал: начало пьяного пения', LEXICON_GROUP.QUEST_HOMETOWN,
        u'Герой начинает петь пьяную песню.',
        [V.HERO]),

        (u'QUEST_HOMETOWN_JOURNAL_REMEMBER_NAMES_DESCRIPTION', 460016, u'Описание: вспоминание имён', LEXICON_GROUP.QUEST_HOMETOWN,
        u'Краткая декларация того, что герой занимается вспоминанием имён.',
        [V.HERO]),

        (u'QUEST_HOMETOWN_JOURNAL_REMEMBER_NAMES_DONOTHING', 460017, u'Журнал: герой вспоминает имена друзей', LEXICON_GROUP.QUEST_HOMETOWN,
        u'фразы, описывающие как герой вспоминает имена знакомых',
        [V.HERO]),

        (u'QUEST_HOMETOWN_JOURNAL_REMEMBER_NAMES_START', 460018, u'Журнал: начало вспоминания имён', LEXICON_GROUP.QUEST_HOMETOWN,
        u'герой начинает вспоминать имена друзей',
        [V.HERO]),

        (u'QUEST_HOMETOWN_JOURNAL_SEARCH_OLD_FRIENDS_DESCRIPTION', 460019, u'Описание: поиск друзей', LEXICON_GROUP.QUEST_HOMETOWN,
        u'Краткая декларация того, что герой ищет друзей.',
        [V.HERO]),

        (u'QUEST_HOMETOWN_JOURNAL_SEARCH_OLD_FRIENDS_DONOTHING', 460020, u'Журнал: герой ищет старых друзей', LEXICON_GROUP.QUEST_HOMETOWN,
        u'Фразы о том, как герой ищет в городе старых друзей',
        [V.HERO]),

        (u'QUEST_HOMETOWN_JOURNAL_SEARCH_OLD_FRIENDS_START', 460021, u'Журнал: начало поиска друзей', LEXICON_GROUP.QUEST_HOMETOWN,
        u'Герой начинает искать старых друзей.',
        [V.HERO]),

        (u'QUEST_HOMETOWN_JOURNAL_STAGGER_STREETS_DESCRIPTION', 460022, u'Описание: шатание по улочкам', LEXICON_GROUP.QUEST_HOMETOWN,
        u'Краткая декларация того, что герой шляется по улочкам.',
        [V.HERO]),

        (u'QUEST_HOMETOWN_JOURNAL_STAGGER_STREETS_DONOTHING', 460023, u'Журнал: шатание по улочкам', LEXICON_GROUP.QUEST_HOMETOWN,
        u'Герой шатается по улочкам',
        [V.HERO]),

        (u'QUEST_HOMETOWN_JOURNAL_STAGGER_STREETS_START', 460024, u'Журнал: начало шатания по улочкам', LEXICON_GROUP.QUEST_HOMETOWN,
        u'Герой отправляется бродить по улочкам города.',
        [V.HERO]),

        (u'QUEST_HOMETOWN_NAME', 460025, u'Название', LEXICON_GROUP.QUEST_HOMETOWN,
        u'Краткое название задания.',
        [V.RECEIVER_POSITION, V.HERO]),

        ]
