# coding: utf-8

from the_tale.common.utils.storage import create_storage_class
from the_tale.common.utils.decorators import lazy_property

from the_tale.game.map.roads.models import Road, Waymark
from the_tale.game.map.roads.prototypes import RoadPrototype, WaymarkPrototype
from the_tale.game.map.roads.exceptions import RoadsException


class RoadsStorage(create_storage_class('roads change time', Road, RoadPrototype, RoadsException)):

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


class WaymarksStorage(create_storage_class('waymarks change time', Waymark, WaymarkPrototype, RoadsException)):

    def __init__(self, *argv, **kwargs):
        super(WaymarksStorage, self).__init__(*argv, **kwargs)
        self._waymarks_map = {}

    def clear(self):
        self._waymarks_map = {}
        del self.average_path_length
        super(WaymarksStorage, self).clear()

    def add_item(self, id_, item):
        super(WaymarksStorage, self).add_item(id_, item)
        del self.average_path_length
        self._waymarks_map[(item.point_from_id, item.point_to_id)] = item

    def look_for_road(self, point_from, point_to):
        self.sync()

        if not isinstance(point_from, int):
            point_from = point_from.id
        if not isinstance(point_to, int):
            point_to = point_to.id

        return  self._waymarks_map.get((point_from, point_to))

    @lazy_property
    def average_path_length(self):
        self.sync()
        total_length = sum(waymark.length for waymark in self.all())
        return float(total_length) / len(self.all())


waymarks_storage = WaymarksStorage()
