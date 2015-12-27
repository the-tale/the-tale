# coding: utf-8

from the_tale.common.utils import storage

from the_tale.game.map.roads.prototypes import RoadPrototype, WaymarkPrototype
from the_tale.game.map.roads import exceptions


class RoadsStorage(storage.Storage):
    SETTINGS_KEY = 'roads change time'
    EXCEPTION = exceptions.RoadsStorageError
    PROTOTYPE = RoadPrototype

    def all_exists_roads(self):
        return [road for road in self.all() if road.exists]

    def get_by_places(self, place_1, place_2):
        for road in self.all():
            if not road.exists:
                continue
            if (road.point_1_id == place_1.id and road.point_2_id == place_2.id or
                road.point_1_id == place_2.id and road.point_2_id == place_1.id):
                return road
        return None


roads_storage = RoadsStorage()


class WaymarksStorage(storage.CachedStorage):
    SETTINGS_KEY = 'waymarks change time'
    EXCEPTION = exceptions.WaymarksStorageError
    PROTOTYPE = WaymarkPrototype

    def _update_cached_data(self, item):
        self._waymarks_map[(item.point_from_id, item.point_to_id)] = item

    def _reset_cache(self):
        self._waymarks_map = {}

    def look_for_road(self, point_from, point_to):
        self.sync()

        if not isinstance(point_from, int):
            point_from = point_from.id
        if not isinstance(point_to, int):
            point_to = point_to.id

        return  self._waymarks_map.get((point_from, point_to))


waymarks_storage = WaymarksStorage()
