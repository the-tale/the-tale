# coding: utf-8

from common.utils.enum import create_enum

RACE = create_enum('RACE', ( ('HUMAN', 0, u'человек'),
                             ('ELF', 1, u'эльф'),
                             ('ORC', 2, u'орк'),
                             ('GOBLIN', 3, u'гоблин'),
                             ('DWARF', 4, u'дварф') ))

RACE_MULTIPLE_VERBOSE = {RACE.HUMAN: u'люди',
                         RACE.ELF: u'эльфы',
                         RACE.ORC: u'орки',
                         RACE.GOBLIN: u'гоблины',
                         RACE.DWARF: u'дварфы'}


ANGEL_ENERGY_REGENERATION_TYPES = create_enum('ANGEL_ENERGY_REGENERATION_TYPES',
                                              ( ('PRAY', 0, u'молитва'),
                                                ('SACRIFICE', 1, u'жертвоприношение'),
                                                ('INCENSE', 2, u'благовония'),
                                                ('SYMBOLS', 3, u'символы'),
                                                ('MEDITATION', 4, u'медитация') ))


CITY_MODIFIERS = create_enum('CITY_MODIFIERS', ( ('TRADE_CENTER', 0, u'Торговый центр'),
                                                 ('CRAFT_CENTER', 1, u'Город мастеров'),
                                                 ('FORT', 2, u'Форт'),
                                                 ('POLITICAL_CENTER', 3, u'Политический центр'),
                                                 ('POLIC', 4, u'Полис'),
                                                 ('RESORT', 5, u'Курорт'),
                                                 ('TRANSPORT_NODE', 6, u'Транспортный узел'),
                                                 ('OUTLAWS', 7, u'Вольница')))
