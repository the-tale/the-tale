# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError

class PersonsError(TheTaleError):
    MSG = u'persons error'


class PersonsPowerError(PersonsError):
    MSG = u'persons power error: %(message)s'


class PersonsStorageError(PersonsError):
    MSG = u'persons power error: %(message)s'


class PersonsFromOnePlaceError(PersonsError):
    MSG = u'can not create connection between persons from one place, persons: %(person_1_id)d, %(person_2_id)d'


class PersonsAlreadyConnectedError(PersonsError):
    MSG = u'persons have been already connected, persons: %(person_1_id)d, %(person_2_id)d'
