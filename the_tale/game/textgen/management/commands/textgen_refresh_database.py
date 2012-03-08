# coding: utf-8
import os
import numbers
import pymorphy

from django.core.management.base import BaseCommand

from dext.utils import s11n

from ...templates import Vocabulary, Dictionary, Template
from ...exceptions import TextgenException
from ...words import WordBase
from ...logic import get_tech_vocabulary, efication
from ...conf import textgen_settings

morph = pymorphy.get_morph(textgen_settings.PYMORPHY_DICTS_DIRECTORY)

class Command(BaseCommand):

    help = 'load texts into databse'

    def handle(self, *args, **options):

        vocabulary = Vocabulary()
        vocabulary.load()

        dictionary = Dictionary()
        dictionary.load()

        tech_vocabulary = get_tech_vocabulary()

        with open(os.path.join(textgen_settings.TEXTS_DIRECTORY, 'words.txt')) as f:
            for string in f:
                word = WordBase.create_from_string(morph, string.decode('utf-8').strip(), tech_vocabulary)
                dictionary.add_word(word)

        for filename in os.listdir(textgen_settings.TEXTS_DIRECTORY):

            if not filename.endswith('.json'):
                continue
            
            if filename == 'vocabulary.json':
                continue

            texts_path = os.path.join(textgen_settings.TEXTS_DIRECTORY, filename)

            if not os.path.isfile(texts_path):
                continue

            group = filename[:-5]

            print 'load %s' % group

            with open(texts_path) as f:
                data = s11n.from_json(f.read())

                if group != data['prefix']:
                    raise Exception('filename MUST be equal to prefix')

                for suffix in data['types']:
                    if suffix == '':
                        raise Exception('type MUST be not equal to empty string')

                for suffix, type_ in data['types'].items():
                    phrase_key = '%s_%s' % (group , suffix)
                    for phrase in type_['phrases']:
                        template_phrase, test_phrase = phrase
                        variables = type_['variables']
                        template = Template.create(morph, template_phrase, available_externals=variables.keys(), tech_vocabulary=tech_vocabulary)
                        
                        vocabulary.add_phrase(phrase_key, template)

                        for value in variables.values():
                            if isinstance(value, numbers.Number):
                                continue
                            word = WordBase.create_from_string(morph, value, tech_vocabulary)
                            dictionary.add_word(word)

                        for string in template.get_internal_words():
                            word = WordBase.create_from_string(morph, string, tech_vocabulary)
                            dictionary.add_word(word)

                        test_result = template.substitute(dictionary, variables)
                        if efication(test_result.lower()) != efication(test_phrase.lower()):
                            print test_phrase
                            print test_result
                            raise TextgenException(u'wrong test render for phrase "%s": "%s"' % (template_phrase, test_result))


        vocabulary.save()
        dictionary.save()
