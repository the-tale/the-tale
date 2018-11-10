
import smart_imports

smart_imports.all()


V = lexicon_relations.VARIABLE


KEYS = [('QUEST_HELP_ACTION_AFTER_SUCCESSED_HELP', 420000, 'Активность: после успешного задания', relations.LEXICON_GROUP.QUEST_HELP,
         'Краткое суммарное описание действий героя, когда он возвращается доложить об успешном выполнении задания.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_HELP_ACTION_INTRO', 420001, 'Активность: интро', relations.LEXICON_GROUP.QUEST_HELP,
         'Краткое суммарное описание действий героя в момент получения задания.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_HELP_ACTOR_INITIATOR', 420002, 'Актёр: инициатор задания', relations.LEXICON_GROUP.QUEST_HELP,
         'Название роли, инициирующей задание.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_HELP_ACTOR_RECEIVER', 420003, 'Актёр: цель задания', relations.LEXICON_GROUP.QUEST_HELP,
         'Название роли, цели задания.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_HELP_DIARY_FINISH_FAILED_ARTIFACT', 420004, 'Дневник: получение награды — провал (артефакт)', relations.LEXICON_GROUP.QUEST_HELP,
         'Герой получает награду за помощь, хотя выполнить задание не удалось (артефакт).',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ARTIFACT], None),

        ('QUEST_HELP_DIARY_FINISH_FAILED_MONEY', 420005, 'Дневник: получение награды — провал (деньги)', relations.LEXICON_GROUP.QUEST_HELP,
         'Герой получает награду за помощь хотя выполнить задание не удалось (деньги).',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.COINS], 'hero#N +coins#G'),

        ('QUEST_HELP_DIARY_FINISH_SUCCESSED_ARTIFACT', 420006, 'Дневник: получение награды (артефакт)', relations.LEXICON_GROUP.QUEST_HELP,
         'Герой получает награду за помощь (артефакт).',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ARTIFACT], None),

        ('QUEST_HELP_DIARY_FINISH_SUCCESSED_MONEY', 420007, 'Дневник: получение награды (деньги)', relations.LEXICON_GROUP.QUEST_HELP,
         'Герой получает награду за помощь (деньги).',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.COINS], 'hero#N +coins#G'),

        ('QUEST_HELP_DIARY_INTRO', 420008, 'Дневник: Начало задания', relations.LEXICON_GROUP.QUEST_HELP,
         'Герой получил задание.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_HELP_JOURNAL_BEFORE_HELP', 420009, 'Журнал: Начало пути', relations.LEXICON_GROUP.QUEST_HELP,
         'Герой отправляется к целевому жителю.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        ('QUEST_HELP_NAME', 420010, 'Название', relations.LEXICON_GROUP.QUEST_HELP,
         'Краткое название задания.',
         [V.DATE, V.TIME, V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),
        ]
