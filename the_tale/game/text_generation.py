# coding: utf-8
import os
import numbers

from django.utils.log import getLogger
from django.conf import settings as project_settings

from dext.utils import s11n

from textgen.words import WordBase
from textgen.templates import Vocabulary, Dictionary

from game.conf import game_settings

_VOCABULARY = None
_DICTIONARY = None
_PHRASES_TYPES = None

logger=getLogger('the-tale.workers.game_logic')

class NamedObject(object):

    def __init__(self, normalized_name):
        self.normalized_name = normalized_name


def prepair_substitution(args):
    result = {}
    for k, v in args.items():
        if isinstance(v, (WordBase, numbers.Number)):
            result[k] = v
        elif isinstance(v, basestring):
            result[k] = get_dictionary().get_word(v)
        else:
            result[k] = v.normalized_name
    return result

def get_text(error_prefix, type_, args):

    vocabulary = get_vocabulary()

    if type_ not in vocabulary:
        if not project_settings.TESTS_RUNNING:
            logger.error('%s: unknown template type: %s' % (error_prefix, type_))
        return None

    args = prepair_substitution(args)
    template = vocabulary.get_random_phrase(type_)

    if template is None:
        # if template type exists but empty
        return None

    return template.substitute(get_dictionary(), args)



def get_vocabulary():
    global _VOCABULARY

    if _VOCABULARY is None:
        _VOCABULARY = Vocabulary()
        if os.path.exists(game_settings.TEXTGEN_STORAGE_VOCABULARY):
            _VOCABULARY.load(storage=game_settings.TEXTGEN_STORAGE_VOCABULARY)

    return _VOCABULARY


def get_dictionary():
    global _DICTIONARY

    if _DICTIONARY is None:
        _DICTIONARY = Dictionary()
        if os.path.exists(game_settings.TEXTGEN_STORAGE_DICTIONARY):
            _DICTIONARY.load(storage=game_settings.TEXTGEN_STORAGE_DICTIONARY)

    return _DICTIONARY

def get_phrases_types():
    global _PHRASES_TYPES

    if _PHRASES_TYPES is None:
        with open(game_settings.TEXTGEN_STORAGE_PHRASES_TYPES, 'r') as f:
            _PHRASES_TYPES = s11n.from_json(f.read())

        _PHRASES_TYPES['_sorted_modules'] = sorted(_PHRASES_TYPES['modules'].keys(), key=lambda key: _PHRASES_TYPES['modules'][key]['name'])

        for module_type, module_data in _PHRASES_TYPES['modules'].items():
            module_data['_sorted_types'] = sorted(module_data['types'].keys(), key=lambda key: module_data['types'][key]['name'])

    return _PHRASES_TYPES

def get_phrase_module_id_by_subtype(subtype):
    for module_type, module_data in _PHRASES_TYPES['modules'].items():
        if subtype in module_data['types']:
            return module_type
