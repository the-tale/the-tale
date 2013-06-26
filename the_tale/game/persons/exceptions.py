# coding: utf-8

from common.utils.exceptions import TheTaleError

class PersonsException(TheTaleError):
    MSG = u'persons error'

# class PlaceEffectsValueError(PersonsException):
#     MSG = u'wrong sum of place effects: %(effects)r'
