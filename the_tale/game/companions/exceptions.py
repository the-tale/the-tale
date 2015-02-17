# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError


class CompanionsError(TheTaleError):
    MSG = u'companions error'

class CompanionsStorageError(CompanionsError):
    MSG = u'companions storage error: %(message)s'

class HealCompanionForNegativeValueError(CompanionsError):
    MSG = u'heal companion for negative value: %(delta)s'
