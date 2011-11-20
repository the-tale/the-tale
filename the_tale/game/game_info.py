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

