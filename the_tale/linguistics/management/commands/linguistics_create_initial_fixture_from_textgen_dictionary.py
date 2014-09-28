# coding: utf-8
import os
import copy

from django.core.management.base import BaseCommand
from django.conf import settings as project_settings

from dext.common.utils import s11n

from textgen.words import WORD_TYPE as T_WORD_TYPE
from textgen.logic import Args

from utg.words import Word, Properties
from utg.logic import get_verbose_to_relations
from utg.relations import WORD_TYPE as U_WORD_TYPE
from utg.relations import FORM as U_FORM

from the_tale.game.text_generation import get_dictionary
from the_tale.linguistics.lexicon import dictionary as lexicon_dictinonary


VERBOSE_TO_RELATIONS = get_verbose_to_relations()


TYPE_RELATIONS = { T_WORD_TYPE.NOUN: U_WORD_TYPE.NOUN,
                   T_WORD_TYPE.ADJECTIVE: U_WORD_TYPE.ADJECTIVE,
                   T_WORD_TYPE.VERB: U_WORD_TYPE.VERB,
                   T_WORD_TYPE.NUMERAL: None,
                   T_WORD_TYPE.NOUN_GROUP: U_WORD_TYPE.NOUN,
                   T_WORD_TYPE.FAKE: None,
                   T_WORD_TYPE.PARTICIPLE: U_WORD_TYPE.PARTICIPLE,
                   T_WORD_TYPE.SHORT_PARTICIPLE: U_WORD_TYPE.PARTICIPLE,
                   T_WORD_TYPE.PRONOUN: U_WORD_TYPE.PRONOUN  }


class Command(BaseCommand):

    help = 'create initial dictionary fixture from textgen dictionary'


    def parse(self, textgen_word):
        if u'ножницы' in textgen_word.forms:
            print 1

        type = TYPE_RELATIONS[textgen_word.TYPE]

        forms = []
        for key in Word.get_keys(type):
            args = Args(*[p.verbose_id for p in key if p])

            form = textgen_word.get_form(args)

            if type.is_VERB and U_FORM.INFINITIVE in key:
                form = u'%s-инфинитив' % form

            forms.append(form)

        properties = Properties(*[VERBOSE_TO_RELATIONS.get(p) for p in textgen_word.properties])

        for property, required in type.properties.iteritems():
            if required and not properties.is_specified(property):
                properties = Properties(properties, property.records[0])

        word = Word(type=type, forms=forms, properties=properties)

        return word


    def handle(self, *args, **options):

        textgen_dict = get_dictionary()

        utg_dictionary = copy.deepcopy(lexicon_dictinonary.DICTIONARY)

        for textgen_key, textgen_word in textgen_dict.data.iteritems():

            if textgen_key.lower() != textgen_key and textgen_key.lower() in textgen_dict:
                continue

            word = self.parse(textgen_word)

            if utg_dictionary.is_word_registered(word.type, word.normal_form()):
                continue

            utg_dictionary.add_word(word)

        for word in utg_dictionary.iterwords():
            if len(word.forms) != Word.get_forms_number(word.type):
                raise Exception('wrong number of forms')

        with open(os.path.join(project_settings.PROJECT_DIR, 'linguistics', 'fixtures', 'dictionary.json'), 'w') as f:
            f.write(s11n.to_json([w.serialize() for w in utg_dictionary.iterwords()], indent=2).encode('utf-8'))
