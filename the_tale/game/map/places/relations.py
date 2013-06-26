# coding: utf-8

from rels.django_staff import DjangoEnum


class BUILDING_STATE(DjangoEnum):
    _records = ( ('WORKING', 0, u'работает'),
                 ('DESTROYED', 1, u'уничтожено') )

class CITY_PARAMETERS(DjangoEnum):
    _records = ( ('PRODUCTION', 0, u'Производство'),
                 ('SAFETY', 1, u'Безопасность'),
                 ('FREEDOM', 2, u'Свободы'),
                 ('TRANSPORT', 3, u'Транспорт'),)


class BUILDING_TYPE(DjangoEnum):
    _records = ( ('SMITHY', 0, u'кузница'),
                 ('FISHING_LODGE', 1, u'домик рыболова'),
                 ('TAILOR_SHOP', 2, u'мастерская портного'),
                 ('SAWMILL', 3, u'лесопилка'),
                 ('HUNTER_HOUSE', 4, u'домик охотника'),
                 ('WATCHTOWER', 5, u'сторожевая башня'),
                 ('TRADING_POST', 6, u'торговый пост'),
                 ('INN', 7, u'трактир'),
                 ('DEN_OF_THIEVE', 8, u'логово вора'),
                 ('FARM', 9, u'ферма'),
                 ('MINE', 10, u'шахта'),
                 ('TEMPLE', 11, u'храм'),
                 ('HOSPITAL', 12, u'больница'),
                 ('LABORATORY', 13, u'лаборатория'),
                 ('SCAFFOLD', 14, u'плаха'),
                 ('MAGE_TOWER', 15, u'башня мага'),
                 ('GUILDHALL', 16, u'ратуша'),
                 ('BUREAU', 17, u'бюро'),
                 ('MANOR', 18, u'поместье'),
                 ('SCENE', 19, u'сцена'),
                 ('MEWS', 20, u'конюшни'),
                 ('RANCH', 21, u'ранчо') )
