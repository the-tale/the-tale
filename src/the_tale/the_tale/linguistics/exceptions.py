# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError


class LinguisticsError(TheTaleError):
    MSG = 'linguistics error'


class DictionaryStorageError(LinguisticsError):
    MSG = 'dictionary storage error: %(message)s'

class LexiconStorageError(LinguisticsError):
    MSG = 'lexicon storage error: %(message)s'

class RestrictionsStorageError(LinguisticsError):
    MSG = 'restrictions storage error: %(message)s'


class NoLexiconKeyError(LinguisticsError):
    MSG = 'no lexicon key was found: %(key)s'
