# coding: utf-8

from game.balance import enums as e

from common.utils.enum import create_enum

RACE_TO_ENERGY_REGENERATION_TYPE  = { e.RACE.HUMAN: e.ANGEL_ENERGY_REGENERATION_TYPES.PRAY,
                                      e.RACE.ELF: e.ANGEL_ENERGY_REGENERATION_TYPES.INCENSE,
                                      e.RACE.ORC: e.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE,
                                      e.RACE.GOBLIN: e.ANGEL_ENERGY_REGENERATION_TYPES.MEDITATION,
                                      e.RACE.DWARF: e.ANGEL_ENERGY_REGENERATION_TYPES.SYMBOLS }


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
    SPEED = 4
    MIGHT_CRIT_CHANCE = 5
    EXPERIENCE = 6
