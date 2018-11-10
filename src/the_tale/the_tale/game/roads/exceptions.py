
import smart_imports

smart_imports.all()


class RoadError(utils_exceptions.TheTaleError):
    MSG = 'road error'


class RoadsStorageError(RoadError):
    MSG = 'roads storage error: %(message)s'


class WaymarksStorageError(RoadError):
    MSG = 'waymarks storage error: %(message)s'


class RoadsAlreadyExistsError(RoadError):
    MSG = 'road (%(start)d, %(stop)d) has already exist'


class WaymarkAlreadyExistsError(RoadError):
    MSG = 'waymark (%(start)d, %(stop)d) has already exist'
