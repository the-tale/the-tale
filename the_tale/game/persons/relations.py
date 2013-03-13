# coding: utf-8
import os

from rels.django_staff import DjangoEnum

from common.utils import xls

from game.balance.enums import RACE, CITY_MODIFIERS


class PERSON_TYPE(DjangoEnum):

    _records = ( ('BLACKSMITH', 0, u'кузнец'),
                 ('FISHERMAN', 1, u'рыбак'),
                 ('TAILOR', 2, u'портной'),
                 ('CARPENTER', 3, u'плотник'),
                 ('HUNTER', 4, u'охотник'),
                 ('WARDEN', 5, u'стражник'),
                 ('MERCHANT', 6, u'торговец'),
                 ('INNKEEPER', 7, u'трактирщик'),
                 ('ROGUE', 8, u'вор'),
                 ('FARMER', 9, u'фермер'),
                 ('MINER', 10, u'шахтёр'),
                 ('PRIEST', 11, u'священник'),
                 ('PHYSICIAN', 12, u'лекарь'),
                 ('ALCHEMIST', 13, u'алхимик'),
                 ('EXECUTIONER', 14, u'палач'),
                 ('MAGICIAN', 15, u'волшебник'),
                 ('MAYOR', 16, u'мэр'),
                 ('BUREAUCRAT', 17, u'бюрократ'),
                 ('ARISTOCRAT', 18, u'аристократ'),
                 ('BARD', 19, u'бард'),
                 ('TAMER', 20, u'дрессировщик'),
                 ('HERDSMAN', 21, u'скотовод') )


_professions_xls_file = os.path.join(os.path.dirname(__file__), 'fixtures/professions.xls')

PROFESSION_TO_RACE_MASTERY = xls.load_table_for_enums(_professions_xls_file, sheet_index=0,
                                                      rows_enum=PERSON_TYPE, columns_enum=RACE,
                                                      data_type=float)

PROFESSION_TO_CITY_MODIFIERS = xls.load_table_for_enums(_professions_xls_file, sheet_index=1,
                                                        rows_enum=PERSON_TYPE, columns_enum=CITY_MODIFIERS,
                                                        data_type=float)
