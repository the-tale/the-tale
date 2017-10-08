
from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [('QUEST_SEARCH_SMITH_ACTION_INTRO', 540000, 'Активность: интро', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        'Краткое суммарное описание действий героя в при начале задания.',
        [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO, V.RECEIVER], None),

        ('QUEST_SEARCH_SMITH_ACTOR_RECEIVER', 540001, 'Актёр: Мастер', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        'Название роли мастера.',
        [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO, V.RECEIVER], None),

        ('QUEST_SEARCH_SMITH_DIARY_INTRO', 540002, 'Дневник: начало задания', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        'Герой получил задание.',
        [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO, V.RECEIVER], None),

        ('QUEST_SEARCH_SMITH_DIARY_QUEST_FAILED', 540003, 'Дневник: подзадание провалено', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        'Герой не смог выполнить задание кузнеца.',
        [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO, V.RECEIVER], None),

        ('QUEST_SEARCH_SMITH_DIARY_QUEST_SUCCESSED', 540004, 'Дневник: подзадание выполнено успешно', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        'Герой успешно выполнил подзадание и собирается возвращаться к кузнецу.',
        [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO, V.RECEIVER], None),

        ('QUEST_SEARCH_SMITH_DIARY_START_QUEST', 540005, 'Дневник: начало подзадания', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        'У героя не хватило денег на оплату работы кузнеца, и он согласился выполнить его задание.',
        [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO, V.RECEIVER], None),

        ('QUEST_SEARCH_SMITH_DIARY_UPGRADE__BUY', 540006, 'Дневник: артефакт создан и экипирован в пустой слот', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        'Мастер создал артефакт и взял деньги. Артефакт экипирован в пустой слот экипировки.',
        [V.DATE, V.TIME, V.HERO, V.RECEIVER, V.RECEIVER_POSITION, V.COINS, V.ARTIFACT], 'hero#N -coins#G'),

        ('QUEST_SEARCH_SMITH_DIARY_UPGRADE__BUY_AND_CHANGE', 540007, 'Дневник: артефакт создан и на него заменён старый артефакт', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        'Мастер создал артефакт и взял деньги. Герой продал старую экипировку и одел новый артефакт.',
        [V.DATE, V.TIME, V.UNEQUIPPED, V.HERO, V.COINS, V.ARTIFACT, V.SELL_PRICE, V.RECEIVER, V.RECEIVER_POSITION], 'hero#N -coins#G +sell_price#G'),

        ('QUEST_SEARCH_SMITH_DIARY_UPGRADE__FAIL', 540008, 'Дневник: артефакт не удалось создать', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        'По каким-то причинам мастер не смог создать артефакт, хоть и взял деньги.',
        [V.DATE, V.TIME, V.RECEIVER_POSITION, V.COINS, V.HERO, V.RECEIVER], 'hero#N -coins#G'),

        ('QUEST_SEARCH_SMITH_DIARY_UPGRADE__REPAIR', 540009, 'Дневник: артефакт починен', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        'Мастер починил артефакт и взял деньги.',
        [V.DATE, V.TIME, V.HERO, V.RECEIVER, V.RECEIVER_POSITION, V.COINS, V.ARTIFACT], 'hero#N -coins#G'),

        ('QUEST_SEARCH_SMITH_DIARY_UPGRADE__SHARP', 540010, 'Дневник: артефакт заточен', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        'Мастер заточил артефакт и взял деньги.',
        [V.DATE, V.TIME, V.HERO, V.RECEIVER, V.RECEIVER_POSITION, V.COINS, V.ARTIFACT], 'hero#N -coins#G'),

        ('QUEST_SEARCH_SMITH_DIARY_UPGRADE_FREE__BUY', 540011, 'Дневник: артефакт создан и экипирован в пустой слот (бесплатно)', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        'Мастер создал артефакт и не взял деньги. Артефакт экипирован в пустой слот экипировки (бесплатно).',
        [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO, V.ARTIFACT, V.RECEIVER], None),

        ('QUEST_SEARCH_SMITH_DIARY_UPGRADE_FREE__BUY_AND_CHANGE', 540012, 'Дневник: артефакт создан и на него заменён старый артефакт (бесплатно)', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        'Мастер создал артефакт и не взял деньги. Герой продал старую экипировку и одел новый артефакт (бесплатно).',
        [V.DATE, V.TIME, V.UNEQUIPPED, V.SELL_PRICE, V.HERO, V.RECEIVER, V.RECEIVER_POSITION, V.ARTIFACT], None),

        ('QUEST_SEARCH_SMITH_DIARY_UPGRADE_FREE__FAIL', 540013, 'Дневник: артефакт не удалось создать (бесплатно)', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        'По каким-то причинам мастер не смог создать артефакт, хоть и не взял деньги (бесплатно).',
        [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO, V.RECEIVER], None),

        ('QUEST_SEARCH_SMITH_DIARY_UPGRADE_FREE__REPAIR', 540014, 'Дневник: артефакт починен (бесплатно)', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        'Мастер починил артефакт и не взял деньги. (бесплатно)',
        [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO, V.ARTIFACT, V.RECEIVER], None),

        ('QUEST_SEARCH_SMITH_DIARY_UPGRADE_FREE__SHARP', 540015, 'Дневник: артефакт заточен (бесплатно)', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        'Мастер заточил артефакт и не взял деньги. (бесплатно)',
        [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO, V.ARTIFACT, V.RECEIVER], None),

        ('QUEST_SEARCH_SMITH_NAME', 540016, 'Название', LEXICON_GROUP.QUEST_SEARCH_SMITH,
        'Краткое название задания.',
        [V.DATE, V.TIME, V.RECEIVER_POSITION, V.HERO, V.RECEIVER], None),

        ]
