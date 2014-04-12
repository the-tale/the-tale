# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError


class RoadError(TheTaleError):
    MSG = u'road error'


class RoadsStorageError(RoadError):
    MSG = u'roads storage error: %(message)s'


class WaymarksStorageError(RoadError):
    MSG = u'waymarks storage error: %(message)s'


class RoadsAlreadyExistsError(RoadError):
    MSG = u'road (%(start)d, %(stop)d) has already exist'
