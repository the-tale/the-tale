
import smart_imports

smart_imports.all()


class MapError(utils_exceptions.TheTaleError):
    MSG = 'map error'


class MapStorageError(MapError):
    MSG = 'map storage error: %(message)s'


class UnknownPowerPointError(MapError):
    MSG = 'try to get uid for unknown power point source %(game_object)r'


class UnknownBuildingTypeError(MapError):
    MSG = 'unknown building type %(building)r'


class UnknownPersonRaceError(MapError):
    MSG = 'unknown person race %(race)r'
