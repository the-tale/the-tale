
import smart_imports

smart_imports.all()


class EmissariesError(utils_exceptions.TheTaleError):
    MSG = 'emissary error'


class EmissariesStorageError(EmissariesError):
    MSG = 'emissaries storage error: %(message)s'


class EventsStorageError(EmissariesError):
    MSG = 'events storage error: %(message)s'


class OnEventCreateError(EmissariesError):
    MSG = 'error on create event: %(message)s'
