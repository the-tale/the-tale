
import smart_imports

smart_imports.all()


class EmissariesError(utils_exceptions.TheTaleError):
    MSG = 'emissary error'


class EmissariesStorageError(EmissariesError):
    MSG = 'emissaries storage error: %(message)s'
