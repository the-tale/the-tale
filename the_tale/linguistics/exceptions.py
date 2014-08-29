# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError


class LinguisticsError(TheTaleError):
    MSG = u'linguistics error'


class DictionaryStorageError(LinguisticsError):
    MSG = u'dictionary storage error: %(message)s'
