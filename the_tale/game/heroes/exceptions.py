# coding: utf-8

from common.utils.exceptions import TheTaleError

class HeroException(TheTaleError):
    MSG = u'hero error'

class WrongPreferenceTypeError(HeroException):
    MSG = u'unknown preference type: "%(preference_type)s"'
