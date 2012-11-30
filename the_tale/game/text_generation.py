# coding: utf-8
import os
import numbers

from dext.utils import s11n

from textgen.words import Fake as FakeWord
from textgen.templates import Vocabulary, Dictionary

from game.conf import game_settings

_VOCABULARY = None
_DICTIONARY = None
_PHRASES_TYPES = None

class NamedObject(object):

    def __init__(self, normalized_name):
        self.normalized_name = normalized_name


def prepair_substitution(args):
    result = {}
    for k, v in args.items():
        if isinstance(v, (FakeWord, numbers.Number)):
            result[k] = v
        else:
            result[k] = v.normalized_name
    return result



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

    return _PHRASES_TYPES
