# coding: utf-8

from common.utils.enum import create_enum

RACE = create_enum('RACE', ( ('HUMAN', 0, u'человек'),
                             ('ELF', 1, u'эльф'),
                             ('ORC', 2, u'орк'),
                             ('GOBLIN', 3, u'гоблин'),
                             ('DWARF', 4, u'дварф') ))

ITEMS_OF_EXPENDITURE = create_enum('ITEMS_OF_EXPENDITURE',
                                   ( ('INSTANT_HEAL', 0, u'лечение'),
                                     ('BUYING_ARTIFACT', 1, u'покупка артефакта'),
                                     ('SHARPENING_ARTIFACT', 2, u'заточка артефакта'),
                                     ('USELESS', 3, u'бесполезные траты'),
                                     ('IMPACT', 4, u'изменение влияния'), ) )

ANGEL_ENERGY_REGENERATION_TYPES = create_enum('ANGEL_ENERGY_REGENERATION_TYPES',
                                              ( ('PRAY', 0, u'молитва'),
                                                ('SACRIFICE', 1, u'жертвоприношение'),
                                                ('INCENSE', 2, u'благовония'),
                                                ('SYMBOLS', 3, u'символы'),
                                                ('MEDITATION', 4, u'медитация') ))

PERSON_TYPE = create_enum('PERSON_TYPE', ( ('BLACKSMITH', 0, u'кузнец'),
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
                                           ('BARD', 19, u'бард') ))
