# coding: utf-8
import os

from django.core.management.base import BaseCommand
from django.conf import settings as project_settings

from dext.common.utils import s11n

from textgen.words import WORD_TYPE as T_WORD_TYPE
from textgen.logic import Args

from utg.words import Word, Properties
from utg.logic import get_verbose_to_relations
from utg.relations import WORD_TYPE as U_WORD_TYPE


from the_tale.game.text_generation import get_dictionary


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
        type = TYPE_RELATIONS[textgen_word.TYPE]

        forms = []
        for key in Word.get_keys(type):
            args = Args(*[p.verbose_id for p in key if p])
            forms.append(textgen_word.get_form(args))

        properties = Properties(*[VERBOSE_TO_RELATIONS.get(p) for p in textgen_word.properties])

        for property, required in type.properties.iteritems():
            if required and not properties.is_specified(property):
                properties.update(property.records[0])

        return Word(type=type, forms=forms, properties=properties)


    def handle(self, *args, **options):

        textgen_dict = get_dictionary()

        words = []

        for textgen_key, textgen_word in textgen_dict.data.iteritems():
            if textgen_key.lower() != textgen_key and textgen_key.lower() in textgen_dict:
                continue

            words.append(self.parse(textgen_word))

        with open(os.path.join(project_settings.PROJECT_DIR, 'linguistics', 'fixtures', 'dictionary.json'), 'w') as f:
            f.write(s11n.to_json([w.serialize() for w in words]).encode('utf-8'))
