# coding: utf-8
import os

from rels import Column
from rels.django_staff import DjangoEnum

from common.utils import xls

from game.balance.enums import RACE, CITY_MODIFIERS
from game.map.places.relations import CITY_PARAMETERS, BUILDING_TYPE


class PERSON_TYPE(DjangoEnum):
    building_type = Column(related_name='person_type')

    _records = ( ('BLACKSMITH',  0, u'кузнец', BUILDING_TYPE.SMITHY),
                 ('FISHERMAN',   1, u'рыбак', BUILDING_TYPE.FISHING_LODGE),
                 ('TAILOR',      2, u'портной', BUILDING_TYPE.TAILOR_SHOP),
                 ('CARPENTER',   3, u'плотник', BUILDING_TYPE.SAWMILL),
                 ('HUNTER',      4, u'охотник', BUILDING_TYPE.HUNTER_HOUSE),
                 ('WARDEN',      5, u'стражник', BUILDING_TYPE.WATCHTOWER),
                 ('MERCHANT',    6, u'торговец', BUILDING_TYPE.TRADING_POST),
                 ('INNKEEPER',   7, u'трактирщик', BUILDING_TYPE.INN),
                 ('ROGUE',       8, u'вор', BUILDING_TYPE.DEN_OF_THIEVE),
                 ('FARMER',      9, u'фермер', BUILDING_TYPE.FARM),
                 ('MINER',       10, u'шахтёр', BUILDING_TYPE.MINE),
                 ('PRIEST',      11, u'священник', BUILDING_TYPE.TEMPLE),
                 ('PHYSICIAN',   12, u'лекарь', BUILDING_TYPE.HOSPITAL),
                 ('ALCHEMIST',   13, u'алхимик', BUILDING_TYPE.LABORATORY),
                 ('EXECUTIONER', 14, u'палач', BUILDING_TYPE.SCAFFOLD),
                 ('MAGICIAN',    15, u'волшебник', BUILDING_TYPE.MAGE_TOWER),
                 ('MAYOR',       16, u'мэр', BUILDING_TYPE.GUILDHALL),
                 ('BUREAUCRAT',  17, u'бюрократ', BUILDING_TYPE.BUREAU),
                 ('ARISTOCRAT',  18, u'аристократ', BUILDING_TYPE.MANOR),
                 ('BARD',        19, u'бард', BUILDING_TYPE.SCENE),
                 ('TAMER',       20, u'дрессировщик', BUILDING_TYPE.MEWS),
                 ('HERDSMAN',    21, u'скотовод', BUILDING_TYPE.RANCH) )


_professions_xls_file = os.path.join(os.path.dirname(__file__), 'fixtures/professions.xls')

PROFESSION_TO_RACE_MASTERY = xls.load_table_for_enums(_professions_xls_file, sheet_index=0,
                                                      rows_enum=PERSON_TYPE, columns_enum=RACE,
                                                      data_type=float)

PROFESSION_TO_CITY_MODIFIERS = xls.load_table_for_enums(_professions_xls_file, sheet_index=1,
                                                        rows_enum=PERSON_TYPE, columns_enum=CITY_MODIFIERS,
                                                        data_type=float)

PROFESSION_TO_CITY_PARAMETERS = xls.load_table_for_enums(_professions_xls_file, sheet_index=2,
                                                         rows_enum=PERSON_TYPE, columns_enum=CITY_PARAMETERS,
                                                         data_type=float)
