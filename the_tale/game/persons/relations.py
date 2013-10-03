# coding: utf-8
import os

from rels import Column
from rels.django_staff import DjangoEnum

from questgen.relations import PROFESSION as QUEST_PROFESSION

from common.utils import xls

from game.balance.enums import RACE, CITY_MODIFIERS
from game.map.places.relations import CITY_PARAMETERS, BUILDING_TYPE


class PERSON_TYPE(DjangoEnum):
    building_type = Column(related_name='person_type')
    quest_profession = Column(unique=False)

    _records = ( ('BLACKSMITH',  0, u'кузнец', BUILDING_TYPE.SMITHY, QUEST_PROFESSION.BLACKSMITH),
                 ('FISHERMAN',   1, u'рыбак', BUILDING_TYPE.FISHING_LODGE, QUEST_PROFESSION.NONE),
                 ('TAILOR',      2, u'портной', BUILDING_TYPE.TAILOR_SHOP, QUEST_PROFESSION.NONE),
                 ('CARPENTER',   3, u'плотник', BUILDING_TYPE.SAWMILL, QUEST_PROFESSION.NONE),
                 ('HUNTER',      4, u'охотник', BUILDING_TYPE.HUNTER_HOUSE, QUEST_PROFESSION.NONE),
                 ('WARDEN',      5, u'стражник', BUILDING_TYPE.WATCHTOWER, QUEST_PROFESSION.NONE),
                 ('MERCHANT',    6, u'торговец', BUILDING_TYPE.TRADING_POST, QUEST_PROFESSION.NONE),
                 ('INNKEEPER',   7, u'трактирщик', BUILDING_TYPE.INN, QUEST_PROFESSION.NONE),
                 ('ROGUE',       8, u'вор', BUILDING_TYPE.DEN_OF_THIEVE, QUEST_PROFESSION.NONE),
                 ('FARMER',      9, u'фермер', BUILDING_TYPE.FARM, QUEST_PROFESSION.NONE),
                 ('MINER',       10, u'шахтёр', BUILDING_TYPE.MINE, QUEST_PROFESSION.NONE),
                 ('PRIEST',      11, u'священник', BUILDING_TYPE.TEMPLE, QUEST_PROFESSION.NONE),
                 ('PHYSICIAN',   12, u'лекарь', BUILDING_TYPE.HOSPITAL, QUEST_PROFESSION.NONE),
                 ('ALCHEMIST',   13, u'алхимик', BUILDING_TYPE.LABORATORY, QUEST_PROFESSION.NONE),
                 ('EXECUTIONER', 14, u'палач', BUILDING_TYPE.SCAFFOLD, QUEST_PROFESSION.NONE),
                 ('MAGICIAN',    15, u'волшебник', BUILDING_TYPE.MAGE_TOWER, QUEST_PROFESSION.NONE),
                 ('MAYOR',       16, u'мэр', BUILDING_TYPE.GUILDHALL, QUEST_PROFESSION.NONE),
                 ('BUREAUCRAT',  17, u'бюрократ', BUILDING_TYPE.BUREAU, QUEST_PROFESSION.NONE),
                 ('ARISTOCRAT',  18, u'аристократ', BUILDING_TYPE.MANOR, QUEST_PROFESSION.NONE),
                 ('BARD',        19, u'бард', BUILDING_TYPE.SCENE, QUEST_PROFESSION.NONE),
                 ('TAMER',       20, u'дрессировщик', BUILDING_TYPE.MEWS, QUEST_PROFESSION.NONE),
                 ('HERDSMAN',    21, u'скотовод', BUILDING_TYPE.RANCH, QUEST_PROFESSION.NONE) )


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
