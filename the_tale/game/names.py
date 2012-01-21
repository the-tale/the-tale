# coding: utf-8

import pynames

from .game_info import RACE

class NamesGenerators(object):

    elven = pynames.elven.DnDNamesGenerator()
    orcish = pynames.mongolian.MongolianNamesGenerator()
    dwarfish = pynames.scandinavian.ScandinavianNamesGenerator()
    goblin = pynames.korean.KoreanNamesGenerator()
    human = pynames.russian.PaganNamesGenerator()

    def get_name(self, race):
        if race == RACE.HUMAN:
            return self.human.get_name_simple()
        if race == RACE.ELF:
            return self.elven.get_name_simple()
        if race == RACE.ORC:
            return self.orcish.get_name_simple()
        if race == RACE.GOBLIN:
            return self.goblin.get_name_simple()
        if race == RACE.DWARF:
            return self.dwarfish.get_name_simple()

generator = NamesGenerators()


