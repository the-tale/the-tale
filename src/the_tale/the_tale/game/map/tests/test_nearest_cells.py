
import smart_imports

smart_imports.all()


class UpdateRoadsListTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

    def test(self):
        road_1 = roads_logic.road_between_places(self.place_1, self.place_2)
        road_2 = roads_logic.road_between_places(self.place_2, self.place_3)

        self.assertEqual(set(map_storage.cells(self.place_1.x, self.place_1.y).roads_ids), {road_1.id})
        self.assertEqual(set(map_storage.cells(self.place_2.x, self.place_2.y).roads_ids), {road_1.id, road_2.id})
        self.assertEqual(set(map_storage.cells(self.place_3.x, self.place_3.y).roads_ids), {road_2.id})
