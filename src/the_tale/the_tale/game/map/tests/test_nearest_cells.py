
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


class GetPlacePoliticPowerOnRoad(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.places = game_logic.create_test_map()

    def test(self):
        road = roads_logic.road_between_places(self.places[0], self.places[1])

        self.assertEqual(len(road.get_cells()), 5)
        self.assertEqual(road.place_1_id, self.places[0].id)

        self.places[0].attrs.politic_radius = 10
        self.places[1].attrs.politic_radius = 5

        dominant_politc_powers = []

        for cell in road.get_cells():
            place, power = map_storage_nearest_cells._get_place_politic_power_on_road(road, *cell)
            dominant_politc_powers.append((place.id, power))

        self.assertEqual(dominant_politc_powers,
                         [(self.places[0].id, 10.0),
                          (self.places[0].id, 7.5),
                          (self.places[0].id, 5.0),
                          (self.places[1].id, 7.5),
                          (self.places[1].id, 10.0)])
