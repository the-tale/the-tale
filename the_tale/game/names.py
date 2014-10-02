# coding: utf-8

import pynames

from utg import words as utg_words
from utg import relations as utg_relations

from the_tale.game import relations


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
        return utg_words.Word(type=utg_relations.WORD_TYPE.NOUN,
                             forms=name_forms,
                             properties=utg_words.Properties(utg_relations.ANIMALITY.ANIMATE,
                                                             gender.utg_id))

    def get_fast_name(self, name, gender=relations.GENDER.MASCULINE):
        from utg import words as utg_words
        from utg import relations as utg_relations

        forms = [name]*12

        name = utg_words.Word(type=utg_relations.WORD_TYPE.NOUN,
                              forms=forms,
                              properties=utg_words.Properties(utg_relations.ANIMALITY.ANIMATE,
                                                              gender.utg_id))

        return name

    def get_test_name(self, name, gender=relations.GENDER.MASCULINE):
        from utg import words as utg_words
        from utg import relations as utg_relations

        forms = [u'%s_%d' % (name, i) for i in xrange(12)]

        name = utg_words.Word(type=utg_relations.WORD_TYPE.NOUN,
                              forms=forms,
                              properties=utg_words.Properties(utg_relations.ANIMALITY.ANIMATE,
                                                              gender.utg_id))

        return name

generator = NamesGenerators()
