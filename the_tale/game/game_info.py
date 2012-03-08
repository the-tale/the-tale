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

GENDER_STR_2_ID = {u'м.р.': GENDER.MASCULINE,
                   u'ж.р.': GENDER.FEMININE,
                   u'ср.р.': GENDER.NEUTER}

GENDER_ID_2_STR = {GENDER.MASCULINE: u'м.р.',
                   GENDER.FEMININE: u'ж.р.',
                   GENDER.NEUTER: u'ср.р.'}
