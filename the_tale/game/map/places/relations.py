# coding: utf-8

from rels import Column
from rels.django_staff import DjangoEnum

from game.persons.relations import PERSON_TYPE


class BUILDING_STATE(DjangoEnum):
    _records = ( ('WORKING', 0, u'работает'),
                 ('DESTROYED', 1, u'уничтожено') )


class BUILDING_TYPE(DjangoEnum):
    person_type = Column(related_name='building_type')

    _records = ( ('SMITHY', 0, u'кузница', PERSON_TYPE.BLACKSMITH),
                 ('FISHING_LODGE', 1, u'домик рыболова', PERSON_TYPE.FISHERMAN),
                 ('TAILOR_SHOP', 2, u'мастерская портного', PERSON_TYPE.TAILOR),
                 ('SAWMILL', 3, u'лесопилка', PERSON_TYPE.CARPENTER),
                 ('HUNTER_HOUSE', 4, u'домик охотника', PERSON_TYPE.HUNTER),
                 ('WATCHTOWER', 5, u'сторожевая башня', PERSON_TYPE.WARDEN),
                 ('TRADING_POST', 6, u'торговый пост', PERSON_TYPE.MERCHANT),
                 ('INN', 7, u'трактир', PERSON_TYPE.INNKEEPER),
                 ('DEN_OF_THIEVE', 8, u'логово вора', PERSON_TYPE.ROGUE),
                 ('FARM', 9, u'ферма', PERSON_TYPE.FARMER),
                 ('MINE', 10, u'шахта', PERSON_TYPE.MINER),
                 ('TEMPLE', 11, u'храм', PERSON_TYPE.PRIEST),
                 ('HOSPITAL', 12, u'больница', PERSON_TYPE.PHYSICIAN),
                 ('LABORATORY', 13, u'лаборатория', PERSON_TYPE.ALCHEMIST),
                 ('SCAFFOLD', 14, u'плаха', PERSON_TYPE.EXECUTIONER),
                 ('MAGE_TOWER', 15, u'башня мага', PERSON_TYPE.MAGICIAN),
                 ('GUILDHALL', 16, u'ратуша', PERSON_TYPE.MAYOR),
                 ('BUREAU', 17, u'бюро', PERSON_TYPE.BUREAUCRAT),
                 ('MANOR', 18, u'поместье', PERSON_TYPE.ARISTOCRAT),
                 ('SCENE', 19, u'сцена', PERSON_TYPE.BARD),
                 ('MEWS', 20, u'конюшни', PERSON_TYPE.TAMER),
                 ('RANCH', 21, u'ранчо', PERSON_TYPE.HERDSMAN) )
