# coding: utf-8

from .templates import Vocabulary, Dictionary

_VOCABULARY = None
_DICTIONARY = None

def get_vocabulary():
    global _VOCABULARY

    if _VOCABULARY is None:
        _VOCABULARY = Vocabulary()
        _VOCABULARY.load()

    return _VOCABULARY


def get_dictionary():
    global _DICTIONARY

    if _DICTIONARY is None:
        _DICTIONARY = Dictionary()
        _DICTIONARY.load()

    return _DICTIONARY
