# coding: utf-8
import os
import numbers
import pymorphy

from django.core.management.base import BaseCommand

from dext.utils import s11n

from ...quests_generator.lines import QUESTS_TYPES
from ...conf import quests_settings

from ....textgen.templates import Vocabulary, Dictionary, Template
from ....textgen.exceptions import TextgenException
from ....textgen.words import WordBase
from ....textgen.logic import get_tech_vocabulary, efication
from ....textgen.conf import textgen_settings

morph = pymorphy.get_morph(textgen_settings.PYMORPHY_DICTS_DIRECTORY)


def add_message(phrase_key, message, variables, vocabulary, tech_vocabulary, dictionary):
    template_phrase, test_phrase = message
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


class Command(BaseCommand):

    help = 'load writers into texts databse'

    def handle(self, *args, **options):

        vocabulary = Vocabulary()
        vocabulary.load()

        dictionary = Dictionary()
        dictionary.load()

        tech_vocabulary = get_tech_vocabulary()

        for filename in os.listdir(quests_settings.WRITERS_DIRECTORY):

            if not filename.endswith('.json'):
                continue
            
            texts_path = os.path.join(quests_settings.WRITERS_DIRECTORY, filename)

            if not os.path.isfile(texts_path):
                continue

            group = filename[:-5]

            print 'load %s' % group

            with open(texts_path) as f:
                data = s11n.from_json(f.read())

                if group != data['prefix']:
                    raise Exception('filename MUST be equal to prefix')

                quest_type = data['quest_type']
                
                if quest_type not in QUESTS_TYPES:
                    raise Exception('unexists quest type')

                if quest_type not in group:
                    raise Exception('quest type MUST be contained in group name')

                variables = data['variables']
                for key, value in variables.items():
                    word = WordBase.create_from_string(morph, value, tech_vocabulary)
                    dictionary.add_word(word)                    

                for base_key, base_message in data['base'].items():
                    phrase_key = '%s_base_%s' % (group, base_key)
                    add_message(phrase_key, base_message, variables, vocabulary, tech_vocabulary, dictionary)

                for action_key, action_message in data['actions'].items():
                    phrase_key = '%s_actions_%s' % (group, action_key)
                    add_message(phrase_key, action_message, variables, vocabulary, tech_vocabulary, dictionary)

                for journal_key, journal_message in data['journal'].items():
                    phrase_key = '%s_journal_%s' % (group, journal_key)
                    add_message(phrase_key, journal_message, variables, vocabulary, tech_vocabulary, dictionary)

                for choice_key, choice_data in data['choices'].items():
                    add_message('%s_choice_%s_question' % (group, choice_key), choice_data['question'], variables, vocabulary, tech_vocabulary, dictionary)
                    for choice, choice_message in choice_data['results'].items():
                        phrase_key = '%s_choice_%s_result_%s' % (group, choice_key, choice)
                        add_message(phrase_key, choice_message, variables, vocabulary, tech_vocabulary, dictionary)


        vocabulary.save()
        dictionary.save()
