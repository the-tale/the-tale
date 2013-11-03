# coding: utf-8

from the_tale.common.utils.testcase import TestCase

from the_tale.game.logic import create_test_map

from the_tale.game.map.conf import map_settings
from the_tale.game.map.storage import map_info_storage


class PrototypeTests(TestCase):

    def setUp(self):
        super(PrototypeTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

    def test_get_dominant_place(self):
        map_info = map_info_storage.item

        coordinates = {}
        coordinates.update(dict( ((x, y), self.place_1.id) for x, y in self.place_1.nearest_cells))
        coordinates.update(dict( ((x, y), self.place_2.id) for x, y in self.place_2.nearest_cells))
        coordinates.update(dict( ((x, y), self.place_3.id) for x, y in self.place_3.nearest_cells))

        for y in xrange(map_settings.HEIGHT):
            for x in xrange(map_settings.WIDTH):
                place_id = coordinates.get((x, y))
                if place_id is None:
                    self.assertEqual(map_info.get_dominant_place(x, y), None)
                else:
                    self.assertEqual(place_id, map_info.get_dominant_place(x, y).id)
