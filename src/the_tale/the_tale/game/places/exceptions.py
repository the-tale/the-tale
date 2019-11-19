
import smart_imports

smart_imports.all()


class PlaceError(utils_exceptions.TheTaleError):
    MSG = 'place error'


class PlacesStorageError(PlaceError):
    MSG = 'places storage error: %(message)s'


class BuildingsStorageError(PlaceError):
    MSG = 'buildings storage error: %(message)s'


class ResourceExchangeStorageError(PlaceError):
    MSG = 'resource exchange storage error: %(message)s'


class EffectsStorageError(PlaceError):
    MSG = 'effects storage error: %(message)s'
