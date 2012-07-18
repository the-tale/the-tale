# coding: utf-8

from common.utils.storage import create_storage_class

from game.map.roads.models import Road
from game.map.roads.prototypes import RoadPrototype
from game.map.roads.exceptions import RoadsException


class RoadsStorage(create_storage_class('roads change time', Road, RoadPrototype, RoadsException)):
    pass

roads_storage = RoadsStorage()
