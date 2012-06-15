# coding: utf-8

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


class ITEMS_OF_EXPENDITURE:
    INSTANT_HEAL = 0
    BUYING_ARTIFACT = 1
    SHARPENING_ARTIFACT = 2
    USELESS = 3
    IMPACT = 4

    ALL = [INSTANT_HEAL, BUYING_ARTIFACT, SHARPENING_ARTIFACT, USELESS, IMPACT]


class ATTRIBUTES:
    INITIATIVE = 0
    HEALTH = 1
    DAMAGE = 2
    BAG_SIZE = 3
