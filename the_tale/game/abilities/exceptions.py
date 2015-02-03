# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError


class AbilitiesError(TheTaleError):
    MSG = u'abilities error'

class UnknownHabitModeError(AbilitiesError):
    MSG = u'action has unknown habit mode: %(mode)s'
