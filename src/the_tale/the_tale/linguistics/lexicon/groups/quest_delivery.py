

import smart_imports

smart_imports.all()


V = lexicon_relations.VARIABLE


KEYS = [('QUEST_DELIVERY_ACTION_DELIVERY_RETURNED', 400000, 'Активность: после убийства вора.', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Краткое суммарное описание действий героя после убийства вора и возвращения письма.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_ACTION_DELIVERY_STEALED', 400001, 'Активность: погоня за вором.', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Краткое суммарное описание действий героя во время погони за вором.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_ACTION_INTRO', 400002, 'Активность: интро', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Краткое суммарное описание действий героя в момент получения задания.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_ACTION_START_DELIVERY', 400003, 'Активность: путешествие к получателю.', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Краткое суммарное описание действий героя при путешествии к получателю.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_ACTION_START_FAKE', 400004, 'Активность: подделка письма.', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Краткое суммарное описание действий героя при путешествии к получателю с поддельным письмом.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_ACTION_START_STEAL', 400005, 'Активность: путешествие к скупщику.', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Краткое суммарное описание действий героя при путешествии к скупщику.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_ACTOR_ANTAGONIST', 400006, 'Актёр: скупщик краденого', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Название роли, скупщику краденого.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_ACTOR_INITIATOR', 400007, 'Актёр: отправитель', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Название роли, инициирующей задание.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_ACTOR_RECEIVER', 400008, 'Актёр: получатель', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Название роли, цели слежки.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_CHOICE_CURRENT_DELIVERY', 400009, 'Выбор: доставка', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Краткая констатация выбора героя в случае доставки предмета.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_CHOICE_CURRENT_DUMMY_LIE', 400010, 'Технический тип', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Технический тип, придумывать фразы для него не надо',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_CHOICE_CURRENT_FAKE', 400011, 'Выбор: подделка', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Краткая констатация выбора героя в случае подделки письма.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_CHOICE_CURRENT_STEAL', 400012, 'Выбор: воровство', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Краткая констатация выбора героя в случае воровства.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_CHOICE_VARIANT_DELIVERY', 400013, 'Вариант выбора: доставка', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Краткое описание варианта выбора, ведущего к доставке предмета получателю.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_CHOICE_VARIANT_DUMMY_LIE', 400014, 'Технический тип', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Технический тип, придумывать фразы для него не надо',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_CHOICE_VARIANT_FAKE', 400015, 'Вариант выбора: подделка', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Краткое описание варианта выбора, ведущего к подделке письма.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_CHOICE_VARIANT_STEAL', 400016, 'Вариант выбора: воровство', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Краткое описание варианта выбора, ведущего к воровству.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_DIARY_DELIVERY_RETURNED', 400017, 'Дневник: вор убит', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Герой убил вора и забрал письмо.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_DIARY_DELIVERY_STEALED', 400018, 'Дневник: письмо украдено', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Герой обнаружил, что письмо украдено.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_DIARY_FINISH_DELIVERY_ARTIFACT', 400019, 'Дневник: награда за доставку (артефакт)', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Герой получает награду за доставку предмета (артефакт).',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.ARTIFACT, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_DIARY_FINISH_DELIVERY_MONEY', 400020, 'Дневник: награда за доставку (деньги)', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Герой получает награду за доставку предмета (деньги).',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.COINS, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], 'hero#N +coins#G'),

        ('QUEST_DELIVERY_DIARY_FINISH_FAKE_DELIVERY_ARTIFACT', 400021, 'Дневник: награда за подделку письма (артефакт)', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Герой получает награду за подделку письма (артефакт).',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.ARTIFACT, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_DIARY_FINISH_FAKE_DELIVERY_MONEY', 400022, 'Дневник: награда за подделку письма (деньги)', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Герой получает награду за подделку письма (деньги).',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.COINS, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], 'hero#N +coins#G'),

        ('QUEST_DELIVERY_DIARY_FINISH_FIGHT_FOR_STEALED__HERO_DIED', 400023, 'Дневник: герой умер во время схватки с вором', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Герой умер по время схватки с вором, задание провалено.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_DIARY_FINISH_STEAL_ARTIFACT', 400024, 'Дневник: награда за воровство (артефакт)', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Герой получает награду за воровство (артефакт).',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.ARTIFACT, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_DIARY_FINISH_STEAL_MONEY', 400025, 'Дневник: награда за воровство (деньги)', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Герой получает награду за воровство (деньги).',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.COINS, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], 'hero#N +coins#G'),

        ('QUEST_DELIVERY_DIARY_INTRO', 400026, 'Дневник: начало задания', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Герой получил задание.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_DIARY_START_DELIVERY', 400027, 'Дневник: выбор доставки', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Герой решил доставить предмет по адресу.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_DIARY_START_FAKE', 400028, 'Дневник: выбор подделки', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Герой решил подделать письмо.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_DIARY_START_STEAL', 400029, 'Дневник: выбор воровства', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Герой решил украсть предмет.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_JOURNAL_DELIVERY_RETURNED', 400030, 'Журнал: вор убит', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Герой убивает вора и забирает письмо.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_JOURNAL_DELIVERY_STEALED', 400031, 'Журнал: обнаружение пропажи письма', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Герой обнаруживает, что письмо украли.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_JOURNAL_FIGHT_THIEF', 400032, 'Журнал: начало сражения с вором', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Герой находит вора и начинает битву с ним.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_JOURNAL_START_DELIVERY', 400033, 'Журнал: отправление к пункту назначения (доставка)', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Герой начинает движение к пункту назначения с целью доставки.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_JOURNAL_START_STEAL', 400034, 'Журнал: отправление к пункту назначения (подделка)', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Герой начинает движение к пункту назначения с поддельным письмом.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ('QUEST_DELIVERY_NAME', 400035, 'Название', relations.LEXICON_GROUP.QUEST_DELIVERY,
         'Краткое название задания.',
         [V.DATE, V.TIME, V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST], None),

        ]
