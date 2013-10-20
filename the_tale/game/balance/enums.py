# coding: utf-8

from common.utils.enum import create_enum


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
