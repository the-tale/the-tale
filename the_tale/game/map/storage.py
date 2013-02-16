# coding: utf-8

from common.utils.storage import create_single_storage_class

from game.map.models import MapInfo
from game.map.prototypes import MapInfoPrototype
from game.map.exceptions import MapException


class MapInfoStorage(create_single_storage_class('map info change time', MapInfo, MapInfoPrototype, MapException)):

    def refresh(self):
        try:
            self._item = MapInfoPrototype(MapInfo.objects.order_by('-turn_number', '-id')[0])
        except IndexError:
            self._item = None


map_info_storage = MapInfoStorage()
