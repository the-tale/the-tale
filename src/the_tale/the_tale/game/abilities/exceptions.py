# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError


class AbilitiesError(TheTaleError):
    MSG = 'abilities error'

class UnknownHabitModeError(AbilitiesError):
    MSG = 'action has unknown habit mode: %(mode)s'
