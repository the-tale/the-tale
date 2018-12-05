
import smart_imports

smart_imports.all()


class RoadBetweenPlacesTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

    def test_road_exists(self):
        road = logic.road_between_places(self.place_1, self.place_2)

        self.assertNotEqual(road, None)
        self.assertEqual({road.point_1_id, road.point_2_id},
                         {self.place_1.id, self.place_2.id})

    def test_road_does_not_exist(self):
        road = logic.road_between_places(self.place_1, self.place_3)

        self.assertEqual(road, None)

    def test_inverted_points(self):
        road_1 = logic.road_between_places(self.place_1, self.place_2)
        road_2 = logic.road_between_places(self.place_2, self.place_1)

        self.assertNotEqual(road_1, None)
        self.assertEqual(road_1.id, road_2.id)


class GetPlacesConnected_toTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

    def test_single_connection(self):
        self.assertEqual(list(logic.get_places_connected_to(self.place_1)),
                         [self.place_2])

    def test_multiple_connections(self):
        self.assertCountEqual(list(logic.get_places_connected_to(self.place_2)),
                              [self.place_1, self.place_3])
