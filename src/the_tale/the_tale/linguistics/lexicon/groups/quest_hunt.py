
from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [('QUEST_HUNT_ACTION_FIGHT', 480000, 'Активность: охота', LEXICON_GROUP.QUEST_HUNT,
        'Краткое суммарное описание действий героя во время преследования добычи.',
        [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO], None),

        ('QUEST_HUNT_ACTION_INTRO', 480001, 'Активность: интро', LEXICON_GROUP.QUEST_HUNT,
        'Краткое суммарное описание действий героя в момент получения задания.',
        [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO], None),

        ('QUEST_HUNT_ACTION_MOVE_TO_HUNT', 480002, 'Активность: путешествие к месту охоты', LEXICON_GROUP.QUEST_HUNT,
        'Краткое суммарное описание действий героя во время путешествия к месту охоты.',
        [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO], None),

        ('QUEST_HUNT_ACTION_RETURN_WITH_PREY', 480003, 'Активность: возвращение с добычей', LEXICON_GROUP.QUEST_HUNT,
        'Краткое суммарное описание действий героя во время возвращения с добычей.',
        [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO], None),

        ('QUEST_HUNT_ACTION_START_TRACK', 480004, 'Активность: выслеживание добычи', LEXICON_GROUP.QUEST_HUNT,
        'Краткое суммарное описание действий героя во время выслеживания добычи.',
        [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO], None),

        ('QUEST_HUNT_ACTOR_RECEIVER_POSITION', 480005, 'Актёр: место охоты', LEXICON_GROUP.QUEST_HUNT,
        'Название роли, места охоты.',
        [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO], None),

        ('QUEST_HUNT_DIARY_INTRO', 480006, 'Дневник: начало задания', LEXICON_GROUP.QUEST_HUNT,
        'Герой получил задание.',
        [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO], None),

        ('QUEST_HUNT_DIARY_SELL_PREY_ARTIFACT', 480007, 'Дневник: награда (артефакт)', LEXICON_GROUP.QUEST_HUNT,
        'Герой получил награду за выполнение задания (артефакт)',
        [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO, V.ARTIFACT], None),

        ('QUEST_HUNT_DIARY_SELL_PREY_MONEY', 480008, 'Дневник: награда (деньги)', LEXICON_GROUP.QUEST_HUNT,
        'Герой получил награду за выполнение задания (деньги)',
        [V.DATE, V.TIME, V.RECEIVER_POSITION, V.COINS, V.HERO], 'hero#N +coins#G'),

        ('QUEST_HUNT_JOURNAL_MOVE_TO_HUNT', 480009, 'Журнал: отправление в места охоты', LEXICON_GROUP.QUEST_HUNT,
        'Герой отправляется в места обитания дичи.',
        [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO], None),

        ('QUEST_HUNT_JOURNAL_RETURN_WITH_PREY', 480010, 'Журнал: возвращение с добычей', LEXICON_GROUP.QUEST_HUNT,
        'Герой отправляется в обратную дорогу, нагруженный добычей',
        [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO], None),

        ('QUEST_HUNT_JOURNAL_START_TRACK', 480011, 'Журнал: выслеживание добычи', LEXICON_GROUP.QUEST_HUNT,
        'Герой нашёл следы дичи.',
        [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO], None),

        ('QUEST_HUNT_NAME', 480012, 'Название', LEXICON_GROUP.QUEST_HUNT,
        'Краткое название задания.',
        [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO], None),

        ]
