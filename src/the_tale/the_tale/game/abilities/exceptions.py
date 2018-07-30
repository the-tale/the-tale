
import smart_imports

smart_imports.all()


class AbilitiesError(utils_exceptions.TheTaleError):
    MSG = 'abilities error'


class UnknownHabitModeError(AbilitiesError):
    MSG = 'action has unknown habit mode: %(mode)s'
