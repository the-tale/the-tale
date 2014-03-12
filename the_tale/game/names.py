# coding: utf-8

import pynames

class NamesGenerators(object):

    elven = pynames.elven.DnDNamesGenerator()
    orcish = pynames.mongolian.MongolianNamesGenerator()
    dwarfish = pynames.scandinavian.ScandinavianNamesGenerator()
    goblin = pynames.korean.KoreanNamesGenerator()
    human = pynames.russian.PaganNamesGenerator()

    def get_name(self, race, gender):
        if race.is_HUMAN:
            return self.human.get_name_simple(gender=gender.pynames_id, language=pynames.LANGUAGE.RU)
        if race.is_ELF:
            return self.elven.get_name_simple(gender=gender.pynames_id, language=pynames.LANGUAGE.RU)
        if race.is_ORC:
            return self.orcish.get_name_simple(gender=gender.pynames_id, language=pynames.LANGUAGE.RU)
        if race.is_GOBLIN:
            return self.goblin.get_name_simple(gender=gender.pynames_id, language=pynames.LANGUAGE.RU)
        if race.is_DWARF:
            return self.dwarfish.get_name_simple(gender=gender.pynames_id, language=pynames.LANGUAGE.EN)

generator = NamesGenerators()
