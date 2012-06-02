# coding: utf-8
import os

from textgen.templates import Vocabulary, Dictionary

from game.conf import game_settings

_VOCABULARY = None
_DICTIONARY = None

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
