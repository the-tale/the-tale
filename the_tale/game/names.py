# coding: utf-8

import pynames

class NamesGenerators(object):

    elven = pynames.elven.DnDNamesGenerator()
    orcish = pynames.mongolian.MongolianNamesGenerator()
    dwarfish = pynames.scandinavian.ScandinavianNamesGenerator()
    goblin = pynames.korean.KoreanNamesGenerator()
    human = pynames.russian.PaganNamesGenerator()

    def get_name(self, race, gender):
        if race._is_HUMAN:
            return self.human.get_name_simple(gender=gender.pynames_id)
        if race._is_ELF:
            return self.elven.get_name_simple(gender=gender.pynames_id)
        if race._is_ORC:
            return self.orcish.get_name_simple(gender=gender.pynames_id)
        if race._is_GOBLIN:
            return self.goblin.get_name_simple(gender=gender.pynames_id)
        if race._is_DWARF:
            return self.dwarfish.get_name_simple(gender=gender.pynames_id)

generator = NamesGenerators()
