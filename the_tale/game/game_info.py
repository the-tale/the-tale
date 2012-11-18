# coding: utf-8

from game.balance import constants as c

from common.utils.enum import create_enum

RACE = create_enum('RACE', ( ('HUMAN', 0, u'человек'),
                             ('ELF', 1, u'эльф'),
                             ('ORC', 2, u'орк'),
                             ('GOBLIN', 3, u'гоблин'),
                             ('DWARF', 4, u'дварф') ))

RACE_TO_ENERGY_REGENERATION_TYPE  = { RACE.HUMAN: c.ANGEL_ENERGY_REGENERATION_TYPES.PRAY,
                                      RACE.ELF: c.ANGEL_ENERGY_REGENERATION_TYPES.INCENSE,
                                      RACE.ORC: c.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE,
                                      RACE.GOBLIN: c.ANGEL_ENERGY_REGENERATION_TYPES.MEDITATION,
                                      RACE.DWARF: c.ANGEL_ENERGY_REGENERATION_TYPES.SYMBOLS }


GENDER = create_enum('GENDER', ( ('MASCULINE', 0, u'мужчина'),
                                 ('FEMININE', 1, u'женщина'),
                                 ('NEUTER', 2, u'оно') ) )


GENDER_STR_2_ID = {u'мр': GENDER.MASCULINE,
                   u'жр': GENDER.FEMININE,
                   u'ср': GENDER.NEUTER}

GENDER_ID_2_STR = {GENDER.MASCULINE: u'мр',
                   GENDER.FEMININE: u'жр',
                   GENDER.NEUTER: u'ср'}

class ATTRIBUTES:
    INITIATIVE = 0
    HEALTH = 1
    DAMAGE = 2
    BAG_SIZE = 3
