# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError

class PersonsError(TheTaleError):
    MSG = 'persons error'


class PersonsPowerError(PersonsError):
    MSG = 'persons power error: %(message)s'


class PersonsStorageError(PersonsError):
    MSG = 'persons power error: %(message)s'


class PersonsFromOnePlaceError(PersonsError):
    MSG = 'can not create connection between persons from one place, persons: %(person_1_id)d, %(person_2_id)d'


class PersonsAlreadyConnectedError(PersonsError):
    MSG = 'persons have been already connected, persons: %(person_1_id)d, %(person_2_id)d'
