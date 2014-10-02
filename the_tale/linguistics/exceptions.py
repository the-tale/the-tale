# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError


class LinguisticsError(TheTaleError):
    MSG = u'linguistics error'


class DictionaryStorageError(LinguisticsError):
    MSG = u'dictionary storage error: %(message)s'

class LexiconStorageError(LinguisticsError):
    MSG = u'lexicon storage error: %(message)s'


class NoLexiconKeyError(LinguisticsError):
    MSG = u'no lexicon key was found: %(key)s'
