
import smart_imports

smart_imports.all()


class RoadBetweenPlacesTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

    def test_road_exists(self):
        road = logic.road_between_places(self.place_1, self.place_2)

        self.assertNotEqual(road, None)
        self.assertEqual({road.place_1_id, road.place_2_id},
                         {self.place_1.id, self.place_2.id})

    def test_road_does_not_exist(self):
        road = logic.road_between_places(self.place_1, self.place_3)

        self.assertEqual(road, None)

    def test_inverted_points(self):
        road_1 = logic.road_between_places(self.place_1, self.place_2)
        road_2 = logic.road_between_places(self.place_2, self.place_1)

        self.assertNotEqual(road_1, None)
        self.assertEqual(road_1.id, road_2.id)


class GetRoadsConnectedToTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

    def test_single_connection(self):
        roads = logic.get_roads_connected_to(self.place_1)

        self.assertEqual(len(roads), 1)

        self.assertIn(self.place_1.id, (roads[0].place_1_id, roads[0].place_2_id))

    def test_multiple_connections(self):
        roads = logic.get_roads_connected_to(self.place_2)

        self.assertEqual(len(roads), 2)

        real_places = {frozenset((road.place_1_id, road.place_2_id)) for road in roads}

        expected_places = {frozenset((self.place_1.id, self.place_2.id)),
                           frozenset((self.place_3.id, self.place_2.id))}

        self.assertEqual(real_places, expected_places)


class GetPlacesConnectedToTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

    def test_single_connection(self):
        self.assertEqual(list(logic.get_places_connected_to(self.place_1)),
                         [self.place_2])

    def test_multiple_connections(self):
        self.assertCountEqual(list(logic.get_places_connected_to(self.place_2)),
                              [self.place_1, self.place_3])


class GetPathCellsTests(utils_testcase.TestCase):

    def test_empty(self):
        self.assertEqual(logic.get_path_cells(1, 2, ''), [(1, 2)])

    def test_complex_path(self):
        self.assertEqual(logic.get_path_cells(10, 20, 'rrddddlluurdd'),
                         [(10, 20),
                          (11, 20),
                          (12, 20),
                          (12, 21),
                          (12, 22),
                          (12, 23),
                          (12, 24),
                          (11, 24),
                          (10, 24),
                          (10, 23),
                          (10, 22),
                          (11, 22),
                          (11, 23),
                          (11, 24)])


class IsPathSuitableForRoad(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

    def test_no_errors(self):
        result = logic.is_path_suitable_for_road(self.place_1.x, self.place_1.y, 'dd')
        self.assertTrue(result.is_NO_ERRORS)

    def test_pass_through_building(self):
        places_logic.create_building(self.place_1.persons[0],
                                     utg_name=game_names.generator().get_test_name(),
                                     position=(self.place_1.x, self.place_1.y + 1))
        result = logic.is_path_suitable_for_road(self.place_1.x, self.place_1.y, 'dd')
        self.assertTrue(result.is_PASS_THROUGH_BUILDING)

    def test_no_start_place(self):
        result = logic.is_path_suitable_for_road(self.place_1.x+1, self.place_1.y, 'ddl')
        self.assertTrue(result.is_NO_START_PLACE)

    def test_no_finish_place(self):
        result = logic.is_path_suitable_for_road(self.place_1.x, self.place_1.y, 'ldd')
        self.assertTrue(result.is_NO_FINISH_PLACE)

    def test_pass_through_place(self):
        result = logic.is_path_suitable_for_road(self.place_1.x, self.place_1.y, 'rdrdll')
        self.assertTrue(result.is_PASS_THROUGH_PLACE)

    def test_cell_not_on_map(self):
        result = logic.is_path_suitable_for_road(self.place_1.x, self.place_1.y, 'l'*10 + 'dd' + 'r'*10)
        self.assertTrue(result.is_CELL_NOT_ON_MAP)

    def test_has_cycles(self):
        result = logic.is_path_suitable_for_road(self.place_1.x, self.place_1.y, 'lduddr')
        self.assertTrue(result.is_HAS_CYCLES)

        result = logic.is_path_suitable_for_road(self.place_1.x, self.place_1.y, 'drruldld')
        self.assertTrue(result.is_HAS_CYCLES)

    def test_wrong_format(self):
        result = logic.is_path_suitable_for_road(self.place_1.x, self.place_1.y, 'lduddr ')
        self.assertTrue(result.is_WRONG_FORMAT)

        result = logic.is_path_suitable_for_road(self.place_1.x, self.place_1.y, 'drruaaldld')
        self.assertTrue(result.is_WRONG_FORMAT)


class CreateRoadTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

    def test_create(self):
        self.assertEqual(logic.road_between_places(self.place_1, self.place_3), None)

        with self.check_changed(lambda: roads_storage.roads._version):
            logic.create_road(self.place_1, self.place_3, path='dd')

        road = logic.road_between_places(self.place_1, self.place_3)

        self.assertEqual(road.path, 'dd')


class DeleteRoadTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

    def test_create(self):
        road = logic.road_between_places(self.place_1, self.place_2)

        self.assertNotEqual(road, None)

        with self.check_changed(lambda: roads_storage.roads._version):
            logic.delete_road(road.id)

        self.assertEqual(logic.road_between_places(self.place_1, self.place_2), None)


class ChangeRoadTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

    def test_create(self):
        road = logic.road_between_places(self.place_1, self.place_2)

        self.assertEqual(road.path, 'rdrd')

        with self.check_changed(lambda: roads_storage.roads._version):
            logic.change_road(road.id, path='rddr')

        road = logic.road_between_places(self.place_1, self.place_2)

        self.assertEqual(road.path, 'rddr')


class RoadSupportCostTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

    def test(self):
        cells = [(1, 1), (1, 2), (1, 3), (1, 4)]

        stabilization_price = 3.0

        def roads_number_getter(x, y):
            return {(1, 1): 1,
                    (1, 2): 2,
                    (1, 3): 1,
                    (1, 4): 4}[(x, y)]

        def magic_getter(x, y):
            return {(1, 1): 2.0,
                    (1, 2): 5.0,
                    (1, 3): 0.5,
                    (1, 4): 1.0}[(x, y)]

        cost = logic.road_support_cost(cells,
                                       stabilization_price=stabilization_price,
                                       roads_number_getter=roads_number_getter,
                                       magic_getter=magic_getter)

        self.assertEqual(cost,
                         3 * 2.0 / 1 +
                         3 * 5.0 / 2 +
                         3 * 0.5 / 1 +
                         3 * 1.0 / 4)
