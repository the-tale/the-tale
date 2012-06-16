# coding: utf-8
import os
import numbers

from textgen.words import Fake as FakeWord
from textgen.templates import Vocabulary, Dictionary

from game.conf import game_settings

_VOCABULARY = None
_DICTIONARY = None

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

    # x = ['---------------']
    # for k,v in result.items():
    #     x.append('%s: %r' % (k, v))
    # from django.utils.log import getLogger
    # getLogger('the-tale.workers.game_logic').error('\n'.join(x))

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
