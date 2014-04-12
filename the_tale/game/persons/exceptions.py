# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError

class PersonsError(TheTaleError):
    MSG = u'persons error'

class PersonsPowerError(PersonsError):
    MSG = u'persons power error: %(message)s'

class PersonsStorageError(PersonsError):
    MSG = u'persons power error: %(message)s'
