
import smart_imports

smart_imports.all()


class RoadsStorage(utils_storage.Storage):
    SETTINGS_KEY = 'roads change time'
    EXCEPTION = exceptions.RoadsStorageError
    PROTOTYPE = prototypes.RoadPrototype

    def all_exists_roads(self):
        return [road for road in self.all() if road.exists]


roads = RoadsStorage()


class WaymarksStorage(utils_storage.CachedStorage):
    SETTINGS_KEY = 'waymarks change time'
    EXCEPTION = exceptions.WaymarksStorageError
    PROTOTYPE = prototypes.WaymarkPrototype

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

        return self._waymarks_map.get((point_from, point_to))


waymarks = WaymarksStorage()
