
import smart_imports

smart_imports.all()


class PrototypeTests(utils_testcase.TestCase):

    def setUp(self):
        super(PrototypeTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

    def test_get_dominant_place(self):
        map_info = storage.map_info.item

        coordinates = {}
        coordinates.update(dict(((x, y), self.place_1.id) for x, y in self.place_1.nearest_cells))
        coordinates.update(dict(((x, y), self.place_2.id) for x, y in self.place_2.nearest_cells))
        coordinates.update(dict(((x, y), self.place_3.id) for x, y in self.place_3.nearest_cells))

        for y in range(conf.settings.HEIGHT):
            for x in range(conf.settings.WIDTH):
                place_id = coordinates.get((x, y))
                if place_id is None:
                    self.assertEqual(map_info.get_dominant_place(x, y), None)
                else:
                    self.assertEqual(place_id, map_info.get_dominant_place(x, y).id)
