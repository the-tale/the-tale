# coding: utf-8

from rels.django import DjangoEnum


class ABILITY_TYPE(DjangoEnum):
    records = ( ('BATTLE', 0, u'боевая'),
                 ('NONBATTLE', 1, u'небоевая'),)


class ABILITY_ACTIVATION_TYPE(DjangoEnum):
    records = ( ('ACTIVE', 0, u'активная'),
                 ('PASSIVE', 1, u'пассивная'), )


class ABILITY_LOGIC_TYPE(DjangoEnum):
    records = ( ('WITHOUT_CONTACT', 0, u'безконтактная'),
                 ('WITH_CONTACT', 1, u'контактная'), )


class ABILITY_AVAILABILITY(DjangoEnum):
   records = ( ('FOR_PLAYERS', 0b0001, u'только для игроков'),
                ('FOR_MONSTERS', 0b0010, u'только для монстров'),
                ('FOR_ALL', 0b0011, u'для всех') )


class DAMAGE_TYPE(DjangoEnum):
   records = ( ('PHYSICAL', 0b0001, u'физический'),
                ('MAGICAL', 0b0010, u'магический'),
                ('MIXED', 0b0011, u'смешанный') )



class MODIFIERS(DjangoEnum):
    records = ( ('INITIATIVE', 0, u'инициатива'),
                ('HEALTH', 1, u'здоровье'),
                ('DAMAGE', 2, u'урон'),
                ('SPEED', 3, u'скорость'),
                ('MIGHT_CRIT_CHANCE', 4, u'шанс критического срабатвания способности Хранителя'),
                ('EXPERIENCE', 5, u'опыт'),
                ('MAX_BAG_SIZE', 6, u'максимальный размер рюкзака'),
                ('POWER', 7, u'сила героя'),
                ('QUEST_MONEY_REWARD', 8, u'денежная награда за выполнение задения'),
                ('BUY_PRICE', 9, u'цена покупки'),
                ('SELL_PRICE', 10, u'цена продажи'),
                ('ITEMS_OF_EXPENDITURE_PRIORITIES', 11, u'приортет трат'),
                ('GET_ARTIFACT_FOR_QUEST', 12, u'может получить артефакты за задания'),
                ('BUY_BETTER_ARTIFACT', 13, u'может купить лучший артефакт') )
