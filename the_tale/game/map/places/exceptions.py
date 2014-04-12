# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError


class PlaceError(TheTaleError):
    MSG = u'place error'


class PlacesPowerError(PlaceError):
    MSG = u'places power error: %(message)s'


class PlacesStorageError(PlaceError):
    MSG = u'places storage error: %(message)s'


class BuildingsStorageError(PlaceError):
    MSG = u'buildings storage error: %(message)s'


class ResourceExchangeStorageError(PlaceError):
    MSG = u'resource exchange storage error: %(message)s'
