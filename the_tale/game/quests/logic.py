# -*- coding: utf-8 -*-
import os
import numbers

from dext.utils.decorators import retry_on_exception
from dext.utils import s11n

from textgen.templates import Dictionary, Vocabulary, Template
from textgen.logic import efication, get_tech_vocabulary
from textgen.words import WordBase
from textgen.exceptions import TextgenException

from game.map.places.models import Place
from game.map.places.prototypes import get_place_by_model

from game.quests.quests_generator.lines import BaseQuestsSource, QUESTS_TYPES
from game.quests.quests_generator.knowlege_base import KnowlegeBase
from game.quests.quests_generator.exceptions import RollBackException
from game.quests.writer import Writer
from game.quests.conf import quests_settings
from game.quests.environment import Environment
from game.quests.prototypes import QuestPrototype

def get_knowlege_base():

    base = KnowlegeBase()

    # fill base
    for place_model in Place.objects.all():
        place = get_place_by_model(place_model)

        place_uuid = 'place_%d' % place.id

        base.add_place(place_uuid, external_data={'id': place.id})

        for person in place.persons:
            person_uuid = 'person_%d' % person.id
            base.add_person(person_uuid, place=place_uuid, external_data={'id': person.id,
                                                                          'name': person.name,
                                                                          'type': person.type,
                                                                          'gender': person.gender,
                                                                          'race': person.race,
                                                                          'place_id': person.place_id})

    base.initialize()

    return base


@retry_on_exception(RollBackException)
def create_random_quest_for_hero(current_time, hero):

    base = get_knowlege_base()

    env = Environment(quests_source=BaseQuestsSource(),
                      writers_constructor=Writer,
                      knowlege_base=base)

    hero_position_uuid = 'place_%d' % hero.position.place.id # expecting place, not road
    env.new_place(place_uuid=hero_position_uuid) #register first place

    env.new_quest(place_start=hero_position_uuid)
    env.create_lines()

    quest_prototype = QuestPrototype.create(current_time, hero, env)

    return quest_prototype


def add_message(morph, phrase_key, message, variables, vocabulary, tech_vocabulary, dictionary):
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


def import_texts(morph, source_dir, tech_vocabulary_path, voc_storage, dict_storage, debug=False):

    vocabulary = Vocabulary()

    if os.path.exists(voc_storage):
        vocabulary.load(storage=voc_storage)

    dictionary = Dictionary()
    if os.path.exists(dict_storage):
        dictionary.load(storage=dict_storage)

    tech_vocabulary = get_tech_vocabulary(tech_vocabulary_path)


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
                add_message(morph, phrase_key, base_message, variables, vocabulary, tech_vocabulary, dictionary)

            for action_key, action_message in data['actions'].items():
                phrase_key = '%s_actions_%s' % (group, action_key)
                add_message(morph, phrase_key, action_message, variables, vocabulary, tech_vocabulary, dictionary)

            for journal_key, journal_message in data['journal'].items():
                phrase_key = '%s_journal_%s' % (group, journal_key)
                add_message(morph, phrase_key, journal_message, variables, vocabulary, tech_vocabulary, dictionary)

            for choice_key, choice_data in data['choices'].items():
                add_message(morph, '%s_choice_%s_question' % (group, choice_key), choice_data['question'], variables, vocabulary, tech_vocabulary, dictionary)
                for choice, choice_message in choice_data['results'].items():
                    phrase_key = '%s_choice_%s_result_%s' % (group, choice_key, choice)
                    add_message(morph, phrase_key, choice_message, variables, vocabulary, tech_vocabulary, dictionary)

    vocabulary.save(storage=voc_storage)
    dictionary.save(storage=dict_storage)
