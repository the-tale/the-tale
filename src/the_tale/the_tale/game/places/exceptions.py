# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError


class PlaceError(TheTaleError):
    MSG = 'place error'


class PlacesStorageError(PlaceError):
    MSG = 'places storage error: %(message)s'


class BuildingsStorageError(PlaceError):
    MSG = 'buildings storage error: %(message)s'


class ResourceExchangeStorageError(PlaceError):
    MSG = 'resource exchange storage error: %(message)s'
