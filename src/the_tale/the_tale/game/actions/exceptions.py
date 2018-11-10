
import smart_imports

smart_imports.all()


class ActionError(utils_exceptions.TheTaleError):
    pass


class WrongHeroMoneySpendType(ActionError):
    MSG = 'wrong hero money spend type: %(spending)s'
