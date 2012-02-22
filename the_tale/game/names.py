# coding: utf-8

import pynames
from pynames.generators import GENDER as PYNAMES_GENDER

from .game_info import RACE
from .journal.template import GENDER

class NamesGenerators(object):

    elven = pynames.elven.DnDNamesGenerator()
    orcish = pynames.mongolian.MongolianNamesGenerator()
    dwarfish = pynames.scandinavian.ScandinavianNamesGenerator()
    goblin = pynames.korean.KoreanNamesGenerator()
    human = pynames.russian.PaganNamesGenerator()

    def get_name(self, race, gender):
        gender = {GENDER.MASCULINE: PYNAMES_GENDER.MALE,
                  GENDER.FEMININE: PYNAMES_GENDER.FEMALE}[gender]
        if race == RACE.HUMAN:
            return self.human.get_name_simple(gender=gender)
        if race == RACE.ELF:
            return self.elven.get_name_simple(gender=gender)
        if race == RACE.ORC:
            return self.orcish.get_name_simple(gender=gender)
        if race == RACE.GOBLIN:
            return self.goblin.get_name_simple(gender=gender)
        if race == RACE.DWARF:
            return self.dwarfish.get_name_simple(gender=gender)

generator = NamesGenerators()


