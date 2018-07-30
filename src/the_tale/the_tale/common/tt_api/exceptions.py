
import smart_imports

smart_imports.all()


class TTAPIError(utils_exceptions.TheTaleError):
    pass


class TTAPIUnexpectedHTTPStatus(TTAPIError):
    MSG = 'Unexpected http status %(status)s for url "%(url)s"'


class TTAPIUnexpectedAPIStatus(TTAPIError):
    MSG = 'Unexpected api status %(status)s for url "%(url)s" with code "%(code)s", message: "%(message)s", details: %(details)s'


class TTBankError(TTAPIError):
    pass


class AutocommitRequiredForAsyncTransaction(TTBankError):
    MSG = 'autocommit required for async transaction'


class TTTimersError(TTAPIError):
    pass


class CanNotCreateTimer(TTTimersError):
    MSG = 'can not create cards timer'


class CanNotChangeTimerSpeed(TTTimersError):
    MSG = 'can not change cards timer speed'
