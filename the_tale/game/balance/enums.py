# coding: utf-8

from the_tale.common.utils.enum import create_enum


ANGEL_ENERGY_REGENERATION_TYPES = create_enum('ANGEL_ENERGY_REGENERATION_TYPES',
                                              ( ('PRAY', 0, u'молитва'),
                                                ('SACRIFICE', 1, u'жертвоприношение'),
                                                ('INCENSE', 2, u'благовония'),
                                                ('SYMBOLS', 3, u'символы'),
                                                ('MEDITATION', 4, u'медитация') ))
