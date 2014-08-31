# coding: utf-8
import time

from the_tale.common.utils import storage

from dext.settings import settings

from the_tale.game.map.prototypes import MapInfoPrototype
from the_tale.game.map import exceptions

from the_tale.game.prototypes import TimePrototype


class MapInfoStorage(storage.SingleStorage):
    SETTINGS_KEY = 'map info change time'
    EXCEPTION = exceptions.MapStorageError
    PROTOTYPE = MapInfoPrototype

    def refresh(self):
        self.clear()

        try:
            self._item = MapInfoPrototype(MapInfoPrototype._model_class.objects.order_by('-turn_number', '-id')[0])
        except IndexError:
            self._item = None

        self._version = settings[self.SETTINGS_KEY]

    def _get_next_version(self):
        return '%d-%f' % (TimePrototype.get_current_turn_number(), time.time())


map_info_storage = MapInfoStorage()
