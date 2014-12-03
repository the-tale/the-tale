# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'QUEST_SEARCH_SMITH_ACTION_INTRO', 540000, u'Активность: интро', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        u'Краткое суммарное описание действий героя в улучшения экипировки.',
        [V.RECEIVER_POSITION, V.HERO, V.RECEIVER]),

        (u'QUEST_SEARCH_SMITH_ACTOR_RECEIVER', 540001, u'Актёр: Мастер', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        u'Название роли мастера.',
        [V.RECEIVER_POSITION, V.HERO, V.RECEIVER]),

        (u'QUEST_SEARCH_SMITH_DIARY_INTRO', 540002, u'Дневник: начало задания', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        u'Герой получил задание.',
        [V.RECEIVER_POSITION, V.HERO, V.RECEIVER]),

        (u'QUEST_SEARCH_SMITH_DIARY_QUEST_FAILED', 540003, u'Дневник: подзадание провалено', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        u'Герой не смог выполнить задание кузнеца.',
        [V.RECEIVER_POSITION, V.HERO, V.RECEIVER]),

        (u'QUEST_SEARCH_SMITH_DIARY_QUEST_SUCCESSED', 540004, u'Дневник: подзадание выполнено успешно', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        u'Герой успешно выполнил подзадание и собирается возвращаться к кузнецу.',
        [V.RECEIVER_POSITION, V.HERO, V.RECEIVER]),

        (u'QUEST_SEARCH_SMITH_DIARY_START_QUEST', 540005, u'Дневник: начало подзадания', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        u'У героя не хватило денег на оплату работы кузнеца, и он согласился выполнить его задание.',
        [V.RECEIVER_POSITION, V.HERO, V.RECEIVER]),

        (u'QUEST_SEARCH_SMITH_DIARY_UPGRADE__BUY', 540006, u'Дневник: артефакт создан и экипирован в пустой слот', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        u'Мастер создал артефакт и взял деньги. Артефакт экипирован в пустой слот экипировки.',
        [V.HERO, V.RECEIVER, V.RECEIVER_POSITION, V.COINS, V.ARTIFACT]),

        (u'QUEST_SEARCH_SMITH_DIARY_UPGRADE__BUY_AND_CHANGE', 540007, u'Дневник: артефакт создан и на него заменён старый артефакт', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        u'Мастер создал артефакт и взял деньги. Герой продал старую экипировку и одел новый артефакт.',
        [V.UNEQUIPPED, V.HERO, V.COINS, V.ARTIFACT, V.SELL_PRICE, V.RECEIVER, V.RECEIVER_POSITION]),

        (u'QUEST_SEARCH_SMITH_DIARY_UPGRADE__FAIL', 540008, u'Дневник: артефакт не удалось создать', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        u'По каким-то причинам мастер не смог создать артефакт, хоть и взял деньги.',
        [V.RECEIVER_POSITION, V.COINS, V.HERO, V.RECEIVER]),

        (u'QUEST_SEARCH_SMITH_DIARY_UPGRADE__REPAIR', 540009, u'Дневник: артефакт починен', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        u'Мастер починил артефакт и взял деньги.',
        [V.HERO, V.RECEIVER, V.RECEIVER_POSITION, V.COINS, V.ARTIFACT]),

        (u'QUEST_SEARCH_SMITH_DIARY_UPGRADE__SHARP', 540010, u'Дневник: артефакт заточен', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        u'Мастер заточил артефакт и взял деньги.',
        [V.HERO, V.RECEIVER, V.RECEIVER_POSITION, V.COINS, V.ARTIFACT]),

        (u'QUEST_SEARCH_SMITH_DIARY_UPGRADE_FREE__BUY', 540011, u'Дневник: артефакт создан и экипирован в пустой слот (бесплатно)', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        u'Мастер создал артефакт и не взял деньги. Артефакт экипирован в пустой слот экипировки (бесплатно).',
        [V.RECEIVER_POSITION, V.HERO, V.ARTIFACT, V.RECEIVER]),

        (u'QUEST_SEARCH_SMITH_DIARY_UPGRADE_FREE__BUY_AND_CHANGE', 540012, u'Дневник: артефакт создан и на него заменён старый артефакт (бесплатно)', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        u'Мастер создал артефакт и не взял деньги. Герой продал старую экипировку и одел новый артефакт (бесплатно).',
        [V.UNEQUIPPED, V.SELL_PRICE, V.HERO, V.RECEIVER, V.RECEIVER_POSITION, V.ARTIFACT]),

        (u'QUEST_SEARCH_SMITH_DIARY_UPGRADE_FREE__FAIL', 540013, u'Дневник: артефакт не удалось создать (бесплатно)', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        u'По каким-то причинам мастер не смог создать артефакт, хоть и не взял деньги (бесплатно).',
        [V.RECEIVER_POSITION, V.HERO, V.RECEIVER]),

        (u'QUEST_SEARCH_SMITH_DIARY_UPGRADE_FREE__REPAIR', 540014, u'Дневник: артефакт починен (бесплатно)', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        u'Мастер починил артефакт и не взял деньги. (бесплатно)',
        [V.RECEIVER_POSITION, V.HERO, V.ARTIFACT, V.RECEIVER]),

        (u'QUEST_SEARCH_SMITH_DIARY_UPGRADE_FREE__SHARP', 540015, u'Дневник: артефакт заточен (бесплатно)', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        u'Мастер заточил артефакт и не взял деньги. (бесплатно)',
        [V.RECEIVER_POSITION, V.HERO, V.ARTIFACT, V.RECEIVER]),

        (u'QUEST_SEARCH_SMITH_NAME', 540016, u'Название', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        u'Краткое название задания.',
        [V.RECEIVER_POSITION, V.HERO, V.RECEIVER]),

        ]
