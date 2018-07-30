
import smart_imports

smart_imports.all()


class CompanionsError(utils_exceptions.TheTaleError):
    MSG = 'companions error'


class CompanionsStorageError(CompanionsError):
    MSG = 'companions storage error: %(message)s'


class HealCompanionForNegativeValueError(CompanionsError):
    MSG = 'heal companion for negative value: %(delta)s'


class NoWeaponsError(CompanionsError):
    MSG = 'companion %(companion_id)s MUST has at least one weapon'
