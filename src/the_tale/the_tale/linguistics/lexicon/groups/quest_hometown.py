# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [('QUEST_HOMETOWN_ACTION_CHATTING', 460000, 'Активность: общение с друзьями', LEXICON_GROUP.QUEST_HOMETOWN,
        'Краткое суммарное описание действий героя во время общения с друзьями.',
        [V.DATE, V.HERO], None),

        ('QUEST_HOMETOWN_ACTION_DRUNK_SONG', 460001, 'Активность: пьяная песня', LEXICON_GROUP.QUEST_HOMETOWN,
        'Краткое суммарное описание действий героя во время пения пьяных песен.',
        [V.DATE, V.HERO], None),

        ('QUEST_HOMETOWN_ACTION_INTRO', 460002, 'Активность: интро', LEXICON_GROUP.QUEST_HOMETOWN,
        'Краткое суммарное описание действий героя в момент получения задания.',
        [V.DATE, V.RECEIVER_POSITION, V.HERO], None),

        ('QUEST_HOMETOWN_ACTION_REMEMBER_NAMES', 460003, 'Активность: вспоминание имён', LEXICON_GROUP.QUEST_HOMETOWN,
        'Краткое описание действий героя во время вспоминания имён жителей города',
        [V.DATE, V.HERO], None),

        ('QUEST_HOMETOWN_ACTION_SEARCH_OLD_FRIENDS', 460004, 'Активность: поиск старых знакомых', LEXICON_GROUP.QUEST_HOMETOWN,
        'Краткое суммарное описание действий героя во время поиска старых друзей.',
        [V.DATE, V.HERO], None),

        ('QUEST_HOMETOWN_ACTION_STAGGER_STREETS', 460005, 'Активность: шатание по улицам', LEXICON_GROUP.QUEST_HOMETOWN,
        'Краткое описание действий героя во время шатания по улицам.',
        [V.DATE, V.HERO], None),

        ('QUEST_HOMETOWN_ACTOR_RECEIVER_POSITION', 460006, 'Актёр: родной город', LEXICON_GROUP.QUEST_HOMETOWN,
        'Название роли, родной город.',
        [V.DATE, V.RECEIVER_POSITION, V.HERO], None),

        ('QUEST_HOMETOWN_DIARY_FINISH_ARTIFACT', 460007, 'Дневник: награда (артефакт)', LEXICON_GROUP.QUEST_HOMETOWN,
        'Герой получает награду за посещение города (артефакт).',
        [V.DATE, V.RECEIVER_POSITION, V.HERO, V.ARTIFACT], None),

        ('QUEST_HOMETOWN_DIARY_FINISH_MONEY', 460008, 'Дневник: награда (деньги)', LEXICON_GROUP.QUEST_HOMETOWN,
        'Герой получает награду за посещение города (деньги).',
        [V.DATE, V.RECEIVER_POSITION, V.COINS, V.HERO], 'hero#N +coins#G'),

        ('QUEST_HOMETOWN_DIARY_INTRO', 460009, 'Дневник: начало задания', LEXICON_GROUP.QUEST_HOMETOWN,
        'Герой получил задание.',
        [V.DATE, V.RECEIVER_POSITION, V.HERO], None),

        ('QUEST_HOMETOWN_JOURNAL_CHATTING_DESCRIPTION', 460010, 'Описание: общение с друзьями', LEXICON_GROUP.QUEST_HOMETOWN,
        'Краткая декларация того, что герой болтает с друзьями.',
        [V.DATE, V.HERO], None),

        ('QUEST_HOMETOWN_JOURNAL_CHATTING_DONOTHING', 460011, 'Журнал: фразы во время болтания с друзьями', LEXICON_GROUP.QUEST_HOMETOWN,
        'Фразы, которые герой говорит, болтая с друзьями',
        [V.DATE, V.HERO], None),

        ('QUEST_HOMETOWN_JOURNAL_CHATTING_START', 460012, 'Журнал: начало разговора с друзьями', LEXICON_GROUP.QUEST_HOMETOWN,
        'Герой начинает болтать с друзьями.',
        [V.DATE, V.HERO], None),

        ('QUEST_HOMETOWN_JOURNAL_DRUNK_SONG_DESCRIPTION', 460013, 'Описание: начало пьяной песни', LEXICON_GROUP.QUEST_HOMETOWN,
        'Краткая декларация того, что герой поёт пьяную песню',
        [V.DATE, V.HERO], None),

        ('QUEST_HOMETOWN_JOURNAL_DRUNK_SONG_DONOTHING', 460014, 'Журнал: пьяное пение', LEXICON_GROUP.QUEST_HOMETOWN,
        'Герой поёт пьяную песню.',
        [V.DATE, V.HERO], None),

        ('QUEST_HOMETOWN_JOURNAL_DRUNK_SONG_START', 460015, 'Журнал: начало пьяного пения', LEXICON_GROUP.QUEST_HOMETOWN,
        'Герой начинает петь пьяную песню.',
        [V.DATE, V.HERO], None),

        ('QUEST_HOMETOWN_JOURNAL_REMEMBER_NAMES_DESCRIPTION', 460016, 'Описание: вспоминание имён', LEXICON_GROUP.QUEST_HOMETOWN,
        'Краткая декларация того, что герой занимается вспоминанием имён.',
        [V.DATE, V.HERO], None),

        ('QUEST_HOMETOWN_JOURNAL_REMEMBER_NAMES_DONOTHING', 460017, 'Журнал: герой вспоминает имена друзей', LEXICON_GROUP.QUEST_HOMETOWN,
        'фразы, описывающие как герой вспоминает имена знакомых',
        [V.DATE, V.HERO], None),

        ('QUEST_HOMETOWN_JOURNAL_REMEMBER_NAMES_START', 460018, 'Журнал: начало вспоминания имён', LEXICON_GROUP.QUEST_HOMETOWN,
        'герой начинает вспоминать имена друзей',
        [V.DATE, V.HERO], None),

        ('QUEST_HOMETOWN_JOURNAL_SEARCH_OLD_FRIENDS_DESCRIPTION', 460019, 'Описание: поиск друзей', LEXICON_GROUP.QUEST_HOMETOWN,
        'Краткая декларация того, что герой ищет друзей.',
        [V.DATE, V.HERO], None),

        ('QUEST_HOMETOWN_JOURNAL_SEARCH_OLD_FRIENDS_DONOTHING', 460020, 'Журнал: герой ищет старых друзей', LEXICON_GROUP.QUEST_HOMETOWN,
        'Фразы о том, как герой ищет в городе старых друзей',
        [V.DATE, V.HERO], None),

        ('QUEST_HOMETOWN_JOURNAL_SEARCH_OLD_FRIENDS_START', 460021, 'Журнал: начало поиска друзей', LEXICON_GROUP.QUEST_HOMETOWN,
        'Герой начинает искать старых друзей.',
        [V.DATE, V.HERO], None),

        ('QUEST_HOMETOWN_JOURNAL_STAGGER_STREETS_DESCRIPTION', 460022, 'Описание: шатание по улочкам', LEXICON_GROUP.QUEST_HOMETOWN,
        'Краткая декларация того, что герой шляется по улочкам.',
        [V.DATE, V.HERO], None),

        ('QUEST_HOMETOWN_JOURNAL_STAGGER_STREETS_DONOTHING', 460023, 'Журнал: шатание по улочкам', LEXICON_GROUP.QUEST_HOMETOWN,
        'Герой шатается по улочкам',
        [V.DATE, V.HERO], None),

        ('QUEST_HOMETOWN_JOURNAL_STAGGER_STREETS_START', 460024, 'Журнал: начало шатания по улочкам', LEXICON_GROUP.QUEST_HOMETOWN,
        'Герой отправляется бродить по улочкам города.',
        [V.DATE, V.HERO], None),

        ('QUEST_HOMETOWN_NAME', 460025, 'Название', LEXICON_GROUP.QUEST_HOMETOWN,
        'Краткое название задания.',
        [V.DATE, V.RECEIVER_POSITION, V.HERO], None),

        ]
