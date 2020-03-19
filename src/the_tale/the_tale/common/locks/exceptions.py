
import smart_imports

smart_imports.all()


class LocksError(utils_exceptions.TheTaleError):
    pass


class LockLostBeforeLockingError(LocksError):
    MSG = 'lock "%(lock)s" lost before locking'
