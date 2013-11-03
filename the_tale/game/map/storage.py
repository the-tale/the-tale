# coding: utf-8
import time

from the_tale.common.utils.storage import create_single_storage_class

from dext.settings import settings

from the_tale.game.map.models import MapInfo
from the_tale.game.map.prototypes import MapInfoPrototype
from the_tale.game.map.exceptions import MapException

from the_tale.game.prototypes import TimePrototype


class MapInfoStorage(create_single_storage_class('map info change time', MapInfo, MapInfoPrototype, MapException)):

    def refresh(self):
        self.clear()

        try:
            self._item = MapInfoPrototype(MapInfo.objects.order_by('-turn_number', '-id')[0])
        except IndexError:
            self._item = None

        self._version = settings[self.SETTINGS_KEY]

    def _get_next_version(self):
        return '%d-%d' % (TimePrototype.get_current_turn_number(), time.time())


map_info_storage = MapInfoStorage()
