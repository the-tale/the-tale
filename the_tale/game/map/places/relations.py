# coding: utf-8

from rels import Column
from rels.django_staff import DjangoEnum

from the_tale.game.balance import constants as c


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



class RESOURCE_EXCHANGE_TYPE(DjangoEnum):
    parameter = Column(unique=False, primary=False, single_type=False)
    amount = Column(unique=False, primary=False, single_type=False)

    PRODUCTION_BASE = int(c.PLACE_GOODS_BONUS / 2)
    SAFETY_BASE = c.PLACE_SAFETY_FROM_BEST_PERSON / 10.0
    TRANSPORT_BASE = c.PLACE_TRANSPORT_FROM_BEST_PERSON / 10.0

    _records = ( ('NONE',  0, u'ничего', None, 0),
                 ('PRODUCTION_SMALL',  1, u'%d продукции' % PRODUCTION_BASE, CITY_PARAMETERS.PRODUCTION, PRODUCTION_BASE),
                 ('PRODUCTION_NORMAL', 2, u'%d продукции' % (PRODUCTION_BASE * 2), CITY_PARAMETERS.PRODUCTION, PRODUCTION_BASE * 2),
                 ('PRODUCTION_LARGE',  3, u'%d продукции' % (PRODUCTION_BASE * 4), CITY_PARAMETERS.PRODUCTION, PRODUCTION_BASE * 4),
                 ('SAFETY_SMALL',      4, u'%.1f%% безопасности' % float(SAFETY_BASE * 100), CITY_PARAMETERS.SAFETY, SAFETY_BASE),
                 ('SAFETY_NORMAL',     5, u'%.1f%% безопасности' % float(SAFETY_BASE * 2 * 100), CITY_PARAMETERS.SAFETY, SAFETY_BASE * 2),
                 ('SAFETY_LARGE',      6, u'%.1f%% безопасности' % float(SAFETY_BASE * 4 * 100), CITY_PARAMETERS.SAFETY, SAFETY_BASE * 4),
                 ('TRANSPORT_SMALL',   7, u'%.1f%% транспорта' % float(TRANSPORT_BASE * 100), CITY_PARAMETERS.TRANSPORT, TRANSPORT_BASE),
                 ('TRANSPORT_NORMAL',  8, u'%.1f%% транспорта' % float(TRANSPORT_BASE * 2 * 100), CITY_PARAMETERS.TRANSPORT, TRANSPORT_BASE * 2),
                 ('TRANSPORT_LARGE',   9, u'%.1f%% транспорта' % float(TRANSPORT_BASE * 4 * 100), CITY_PARAMETERS.TRANSPORT, TRANSPORT_BASE * 4) )
