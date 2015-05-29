# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'QUEST_DELIVERY_ACTION_DELIVERY_RETURNED', 400000, u'Активность: после убийства вора.', LEXICON_GROUP.QUEST_DELIVERY,
        u'Краткое суммарное описание действий героя после убийства вора и возвращения письма.',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_ACTION_DELIVERY_STEALED', 400001, u'Активность: погоня за вором.', LEXICON_GROUP.QUEST_DELIVERY,
        u'Краткое суммарное описание действий героя во время погони за вором.',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_ACTION_INTRO', 400002, u'Активность: интро', LEXICON_GROUP.QUEST_DELIVERY,
        u'Краткое суммарное описание действий героя в момент получения задания.',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_ACTION_START_DELIVERY', 400003, u'Активность: путешествие к получателю.', LEXICON_GROUP.QUEST_DELIVERY,
        u'Краткое суммарное описание действий героя при путешествии к получателю.',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_ACTION_START_FAKE', 400004, u'Активность: подделка письма.', LEXICON_GROUP.QUEST_DELIVERY,
        u'Краткое суммарное описание действий героя при путешествии к получателю с поддельным письмом.',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_ACTION_START_STEAL', 400005, u'Активность: путешествие к скупщику.', LEXICON_GROUP.QUEST_DELIVERY,
        u'Краткое суммарное описание действий героя при путешествии к скупщику.',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_ACTOR_ANTAGONIST', 400006, u'Актёр: скупщик краденого', LEXICON_GROUP.QUEST_DELIVERY,
        u'Название роли, скупщику краденого.',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_ACTOR_INITIATOR', 400007, u'Актёр: отправитель', LEXICON_GROUP.QUEST_DELIVERY,
        u'Название роли, инициирующей задание.',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_ACTOR_RECEIVER', 400008, u'Актёр: получатель', LEXICON_GROUP.QUEST_DELIVERY,
        u'Название роли, цели слежки.',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_CHOICE_CURRENT_DELIVERY', 400009, u'Выбор: доставка', LEXICON_GROUP.QUEST_DELIVERY,
        u'Краткая констатация выбора героя в случае доставки предмета.',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_CHOICE_CURRENT_DUMMY_LIE', 400010, u'Технический тип', LEXICON_GROUP.QUEST_DELIVERY,
        u'Технический тип, придумывать фразы для него не надо',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_CHOICE_CURRENT_FAKE', 400011, u'Выбор: подделка', LEXICON_GROUP.QUEST_DELIVERY,
        u'Краткая констатация выбора героя в случае подделки письма.',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_CHOICE_CURRENT_STEAL', 400012, u'Выбор: воровство', LEXICON_GROUP.QUEST_DELIVERY,
        u'Краткая констатация выбора героя в случае воровства.',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_CHOICE_VARIANT_DELIVERY', 400013, u'Вариант выбора: доставка', LEXICON_GROUP.QUEST_DELIVERY,
        u'Краткое описание варианта выбора, ведущего к доставке предмета получателю.',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_CHOICE_VARIANT_DUMMY_LIE', 400014, u'Технический тип', LEXICON_GROUP.QUEST_DELIVERY,
        u'Технический тип, придумывать фразы для него не надо',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_CHOICE_VARIANT_FAKE', 400015, u'Вариант выбора: подделка', LEXICON_GROUP.QUEST_DELIVERY,
        u'Краткое описание варианта выбора, ведущего к подделке письма.',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_CHOICE_VARIANT_STEAL', 400016, u'Вариант выбора: воровство', LEXICON_GROUP.QUEST_DELIVERY,
        u'Краткое описание варианта выбора, ведущего к воровству.',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_DIARY_DELIVERY_RETURNED', 400017, u'Дневник: вор убит', LEXICON_GROUP.QUEST_DELIVERY,
        u'Герой убил вора и забрал письмо.',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_DIARY_DELIVERY_STEALED', 400018, u'Дневник: письмо украдено', LEXICON_GROUP.QUEST_DELIVERY,
        u'Герой обнаружил, что письмо украдено.',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_DIARY_FINISH_DELIVERY_ARTIFACT', 400019, u'Дневник: награда за доставку (артефакт)', LEXICON_GROUP.QUEST_DELIVERY,
        u'Герой получает награду за доставку предмета (артефакт).',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.ARTIFACT, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_DIARY_FINISH_DELIVERY_MONEY', 400020, u'Дневник: награда за доставку (деньги)', LEXICON_GROUP.QUEST_DELIVERY,
        u'Герой получает награду за доставку предмета (деньги).',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.COINS, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_DIARY_FINISH_FAKE_DELIVERY_ARTIFACT', 400021, u'Дневник: награда за подделку письма (артефакт)', LEXICON_GROUP.QUEST_DELIVERY,
        u'Герой получает награду за подделку письма (артефакт).',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.ARTIFACT, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_DIARY_FINISH_FAKE_DELIVERY_MONEY', 400022, u'Дневник: награда за подделку письма (деньги)', LEXICON_GROUP.QUEST_DELIVERY,
        u'Герой получает награду за подделку письма (деньги).',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.COINS, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_DIARY_FINISH_FIGHT_FOR_STEALED__HERO_DIED', 400023, u'Дневник: герой умер во время схватки с вором', LEXICON_GROUP.QUEST_DELIVERY,
        u'Герой умер по время схватки с вором, задание провалено.',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_DIARY_FINISH_STEAL_ARTIFACT', 400024, u'Дневник: награда за воровство (артефакт)', LEXICON_GROUP.QUEST_DELIVERY,
        u'Герой получает награду за воровство (артефакт).',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.ARTIFACT, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_DIARY_FINISH_STEAL_MONEY', 400025, u'Дневник: награда за воровство (деньги)', LEXICON_GROUP.QUEST_DELIVERY,
        u'Герой получает награду за воровство (деньги).',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.COINS, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_DIARY_INTRO', 400026, u'Дневник: начало задания', LEXICON_GROUP.QUEST_DELIVERY,
        u'Герой получил задание.',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_DIARY_START_DELIVERY', 400027, u'Дневник: выбор доставки', LEXICON_GROUP.QUEST_DELIVERY,
        u'Герой решил доставить предмет по адресу.',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_DIARY_START_FAKE', 400028, u'Дневник: выбор подделки', LEXICON_GROUP.QUEST_DELIVERY,
        u'Герой решил подделать письмо.',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_DIARY_START_STEAL', 400029, u'Дневник: выбор воровства', LEXICON_GROUP.QUEST_DELIVERY,
        u'Герой решил украсть предмет.',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_JOURNAL_DELIVERY_RETURNED', 400030, u'Журнал: вор убит', LEXICON_GROUP.QUEST_DELIVERY,
        u'Герой убивает вора и забирает письмо.',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_JOURNAL_DELIVERY_STEALED', 400031, u'Журнал: обнаружение пропажи письма', LEXICON_GROUP.QUEST_DELIVERY,
        u'Герой обнаруживает, что письмо украли.',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_JOURNAL_FIGHT_THIEF', 400032, u'Журнал: начало сражения с вором', LEXICON_GROUP.QUEST_DELIVERY,
        u'Герой находит вора и начинает битву с ним.',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_JOURNAL_START_DELIVERY', 400033, u'Журнал: отправление к пункту назначения (доставка)', LEXICON_GROUP.QUEST_DELIVERY,
        u'Герой начинает движение к пункту назначения с целью доставки.',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_JOURNAL_START_STEAL', 400034, u'Журнал: отправление к пункту назначения (подделка)', LEXICON_GROUP.QUEST_DELIVERY,
        u'Герой начинает движение к пункту назначения с поддельным письмом.',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        (u'QUEST_DELIVERY_NAME', 400035, u'Название', LEXICON_GROUP.QUEST_DELIVERY,
        u'Краткое название задания.',
        [V.INITIATOR, V.HERO, V.ANTAGONIST_POSITION, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ANTAGONIST]),

        ]
