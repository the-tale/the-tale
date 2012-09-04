# coding: utf-8

from game.balance import constants as c

class RACE:
    HUMAN = 0
    ELF = 1
    ORC = 2
    GOBLIN = 3
    DWARF = 4

RACE_CHOICES = ( (RACE.HUMAN, u'человек'),
                 (RACE.ELF, u'эльф'),
                 (RACE.ORC, u'орк'),
                 (RACE.GOBLIN, u'гоблин'),
                 (RACE.DWARF, u'дворф') )

RACE_DICT = dict(RACE_CHOICES)

RACE_TO_ENERGY_REGENERATION_TYPE  = { RACE.HUMAN: c.ANGEL_ENERGY_REGENERATION_TYPES.PRAY,
                                      RACE.ELF: c.ANGEL_ENERGY_REGENERATION_TYPES.INCENSE,
                                      RACE.ORC: c.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE,
                                      RACE.GOBLIN: c.ANGEL_ENERGY_REGENERATION_TYPES.MEDITATION,
                                      RACE.DWARF: c.ANGEL_ENERGY_REGENERATION_TYPES.SYMBOLS }


class GENDER:
    MASCULINE = 0
    FEMININE = 1
    NEUTER = 2

GENDER_CHOICES = ( (GENDER.MASCULINE, u'мужской род'),
                   (GENDER.FEMININE, u'женский род'),
                   (GENDER.NEUTER, u'средний род') )

GENDER_DICT_USERFRIENDLY = {GENDER.MASCULINE: u'мужчина',
                            GENDER.FEMININE: u'женщина',
                            GENDER.NEUTER: u'оно'}

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
