# coding: utf-8

from common.utils.storage import create_storage_class

from game.map.roads.models import Road, Waymark
from game.map.roads.prototypes import RoadPrototype, WaymarkPrototype
from game.map.roads.exceptions import RoadsException


class RoadsStorage(create_storage_class('roads change time', Road, RoadPrototype, RoadsException)):

    def all_exists_roads(self):
        return [road for road in self.all() if road.exists]

roads_storage = RoadsStorage()


class WaymarksStorage(create_storage_class('waymarks change time', Waymark, WaymarkPrototype, RoadsException)):

    def __init__(self, *argv, **kwargs):
        self._waymarks_map = {}
        super(WaymarksStorage, self).__init__(*argv, **kwargs)

    def clear(self):
        self._waymarks_map = {}
        super(WaymarksStorage, self).clear()

    def add_item(self, id_, item):
        super(WaymarksStorage, self).add_item(id_, item)
        self._waymarks_map[(item.point_from_id, item.point_to_id)] = item

    def look_for_road(self, point_from, point_to):
        self.sync()

        if not isinstance(point_from, int):
            point_from = point_from.id
        if not isinstance(point_to, int):
            point_to = point_to.id

        return  self._waymarks_map.get((point_from, point_to))


waymarks_storage = WaymarksStorage()
