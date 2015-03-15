# coding: utf-8
import os

from rels import Column
from rels.django import DjangoEnum

from questgen import relations as questgen_relations

from the_tale.common.utils import xls

from the_tale.game.relations import RACE
from the_tale.game.map.places.relations import CITY_PARAMETERS, BUILDING_TYPE, CITY_MODIFIERS


class PERSON_STATE(DjangoEnum):
    records = ( ('IN_GAME', 0,  u'в игре'),
                ('OUT_GAME', 1, u'вне игры'),
                ('REMOVED', 2, u'удален') )

class PERSON_TYPE(DjangoEnum):
    building_type = Column(related_name='person_type')
    quest_profession = Column(unique=False)

    records = ( ('BLACKSMITH',  0, u'кузнец', BUILDING_TYPE.SMITHY, questgen_relations.PROFESSION.BLACKSMITH),
                 ('FISHERMAN',   1, u'рыбак', BUILDING_TYPE.FISHING_LODGE, questgen_relations.PROFESSION.NONE),
                 ('TAILOR',      2, u'портной', BUILDING_TYPE.TAILOR_SHOP, questgen_relations.PROFESSION.NONE),
                 ('CARPENTER',   3, u'плотник', BUILDING_TYPE.SAWMILL, questgen_relations.PROFESSION.NONE),
                 ('HUNTER',      4, u'охотник', BUILDING_TYPE.HUNTER_HOUSE, questgen_relations.PROFESSION.NONE),
                 ('WARDEN',      5, u'стражник', BUILDING_TYPE.WATCHTOWER, questgen_relations.PROFESSION.NONE),
                 ('MERCHANT',    6, u'торговец', BUILDING_TYPE.TRADING_POST, questgen_relations.PROFESSION.NONE),
                 ('INNKEEPER',   7, u'трактирщик', BUILDING_TYPE.INN, questgen_relations.PROFESSION.NONE),
                 ('ROGUE',       8, u'вор', BUILDING_TYPE.DEN_OF_THIEVE, questgen_relations.PROFESSION.ROGUE),
                 ('FARMER',      9, u'фермер', BUILDING_TYPE.FARM, questgen_relations.PROFESSION.NONE),
                 ('MINER',       10, u'шахтёр', BUILDING_TYPE.MINE, questgen_relations.PROFESSION.NONE),
                 ('PRIEST',      11, u'священник', BUILDING_TYPE.TEMPLE, questgen_relations.PROFESSION.NONE),
                 ('PHYSICIAN',   12, u'лекарь', BUILDING_TYPE.HOSPITAL, questgen_relations.PROFESSION.NONE),
                 ('ALCHEMIST',   13, u'алхимик', BUILDING_TYPE.LABORATORY, questgen_relations.PROFESSION.NONE),
                 ('EXECUTIONER', 14, u'палач', BUILDING_TYPE.SCAFFOLD, questgen_relations.PROFESSION.NONE),
                 ('MAGICIAN',    15, u'волшебник', BUILDING_TYPE.MAGE_TOWER, questgen_relations.PROFESSION.NONE),
                 ('MAYOR',       16, u'мэр', BUILDING_TYPE.GUILDHALL, questgen_relations.PROFESSION.NONE),
                 ('BUREAUCRAT',  17, u'бюрократ', BUILDING_TYPE.BUREAU, questgen_relations.PROFESSION.NONE),
                 ('ARISTOCRAT',  18, u'аристократ', BUILDING_TYPE.MANOR, questgen_relations.PROFESSION.NONE),
                 ('BARD',        19, u'бард', BUILDING_TYPE.SCENE, questgen_relations.PROFESSION.NONE),
                 ('TAMER',       20, u'дрессировщик', BUILDING_TYPE.MEWS, questgen_relations.PROFESSION.NONE),
                 ('HERDSMAN',    21, u'скотовод', BUILDING_TYPE.RANCH, questgen_relations.PROFESSION.NONE) )


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

class SOCIAL_CONNECTION_TYPE(DjangoEnum):
    questgen_type = Column()
    records = ( ('PARTNER', 0, u'партнёр', questgen_relations.SOCIAL_RELATIONS.PARTNER),
                ('CONCURRENT', 1, u'конкурент', questgen_relations.SOCIAL_RELATIONS.CONCURRENT), )

class SOCIAL_CONNECTION_STATE(DjangoEnum):
    records = ( ('IN_GAME', 0, u'в игре'),
                ('OUT_GAME', 1, u'вне игры'), )
