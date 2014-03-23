# coding: utf-8

import pynames

from textgen.words import Noun


class NamesGenerators(object):

    elven = pynames.elven.DnDNamesGenerator()
    orcish = pynames.mongolian.MongolianNamesGenerator()
    dwarfish = pynames.scandinavian.ScandinavianNamesGenerator()
    goblin = pynames.korean.KoreanNamesGenerator()
    human = pynames.russian.PaganNamesGenerator()

    def _get_name(self, race, gender):
        if race.is_HUMAN:
            return self.human.get_name(genders=[gender.pynames_id])
        if race.is_ELF:
            return self.elven.get_name(genders=[gender.pynames_id])
        if race.is_ORC:
            return self.orcish.get_name(genders=[gender.pynames_id])
        if race.is_GOBLIN:
            return self.goblin.get_name(genders=[gender.pynames_id])
        if race.is_DWARF:
            return self.dwarfish.get_name(genders=[gender.pynames_id])

    def get_name(self, race, gender):
        name_forms = self._get_name(race, gender).get_forms_for(gender=gender.pynames_id, language=pynames.LANGUAGE.RU)
        return Noun(normalized=name_forms[0],
                    forms=name_forms,
                    properties=(gender.text_id,))

generator = NamesGenerators()
