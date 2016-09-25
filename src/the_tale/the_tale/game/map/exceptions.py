# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError


class MapError(TheTaleError):
    MSG = u'map error'


class MapStorageError(MapError):
    MSG = u'map storage error: %(message)s'


class UnknownPowerPointError(MapError):
    MSG = u'try to get uid for unknown power point source %(game_object)r'

class UnknownBuildingTypeError(MapError):
    MSG = u'unknown building type %(building)r'

class UnknownPersonRaceError(MapError):
    MSG = u'unknown person race %(race)r'
