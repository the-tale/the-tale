
import smart_imports

smart_imports.all()


class SimpleTravelCost:

    def __init__(self, map):
        self.map = map
        self.best_cost = min(min(*row) for row in map)

    def get_cost(self, x_1, y_1, x_2, y_2):
        return (self.map[y_1][x_1] + self.map[y_2][x_2]) / 2


class SimpleRestoreTravelCost:

    def __init__(self):
        pass

    def get_cost(self, x_1, y_1, x_2, y_2):
        return 1


class NeighboursCoordinatesTests(utils_testcase.TestCase):

    def test_borders(self):
        cells = set(pathfinder.neighbours_coordinates(x=0, y=0, width=10, height=10))
        self.assertEqual(cells, {(1, 0), (0, 1)})

        cells = set(pathfinder.neighbours_coordinates(x=9, y=9, width=10, height=10))
        self.assertEqual(cells, {(9, 8), (8, 9)})

    def test_all_neighbource(self):
        cells = set(pathfinder.neighbours_coordinates(x=5, y=5, width=10, height=10))
        self.assertEqual(cells, {(4, 5), (5, 4), (6, 5), (5, 6)})


class CellTravelCostTests(utils_testcase.TestCase):

    def test__constants_not_changed(self):
        cost = pathfinder.cell_travel_cost(transport=0.2, safety=0.75, expected_battle_complexity=1.0)
        self.assertEqual(cost, 1.0526315789473684)

    def test_battle_complexity(self):
        cost_1 = pathfinder.cell_travel_cost(transport=0.2, safety=0.75, expected_battle_complexity=1.0)
        cost_2 = pathfinder.cell_travel_cost(transport=0.2, safety=0.75, expected_battle_complexity=1.5)
        cost_3 = pathfinder.cell_travel_cost(transport=0.2, safety=0.75, expected_battle_complexity=0.5)

        self.assertTrue(cost_2 < cost_1 < cost_3)

    def test_safety(self):
        cost_1 = pathfinder.cell_travel_cost(transport=0.2, safety=0.75, expected_battle_complexity=1.0)
        cost_2 = pathfinder.cell_travel_cost(transport=0.2, safety=1.0, expected_battle_complexity=1.0)
        cost_3 = pathfinder.cell_travel_cost(transport=0.2, safety=0.5, expected_battle_complexity=1.0)

        self.assertTrue(cost_2 < cost_1 < cost_3)

    def test_transport(self):
        cost_1 = pathfinder.cell_travel_cost(transport=0.75, safety=0.75, expected_battle_complexity=1.0)
        cost_2 = pathfinder.cell_travel_cost(transport=1.0, safety=0.75, expected_battle_complexity=1.0)
        cost_3 = pathfinder.cell_travel_cost(transport=0.5, safety=0.75, expected_battle_complexity=1.0)

        self.assertTrue(cost_2 < cost_1 < cost_3)


class TravelCostTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

    def test(self):
        cell_1 = map_storage.cells(self.place_1.x, self.place_1.y)
        cell_2 = map_storage.cells(self.place_1.x + 1, self.place_1.y - 1)

        self.assertNotEqual(cell_1.transport, cell_2.transport)

        cost_1 = pathfinder.travel_cost(cell_1, cell_1, expected_battle_complexity=1.0)
        cost_2 = pathfinder.travel_cost(cell_2, cell_2, expected_battle_complexity=1.0)

        cost_1_2 = pathfinder.travel_cost(cell_1, cell_2, expected_battle_complexity=1.0)
        cost_2_1 = pathfinder.travel_cost(cell_2, cell_1, expected_battle_complexity=1.0)

        self.assertEqual(cost_1_2, cost_2_1)
        self.assertEqual(cost_1_2, (cost_1 + cost_2) / 2)


class TravelCostCacheTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.cache = pathfinder.TravelCost(map=map_storage.cells.get_map(),
                                           expected_battle_complexity=1.2)

    @mock.patch('the_tale.game.map.storage.CellInfo.transport', 3)
    @mock.patch('the_tale.game.map.storage.CellInfo.safety', 4)
    def test_initialization(self):
        cache = pathfinder.TravelCost(map=map_storage.cells.get_map(),
                                      expected_battle_complexity=1.2)

        self.assertEqual(cache.expected_battle_complexity, 1.2)
        self.assertEqual(cache.best_cost,
                         pathfinder.cell_travel_cost(transport=3,
                                                     safety=4,
                                                     expected_battle_complexity=1.2))
        self.assertEqual(cache._cache, {})

    def test_get_cost(self):
        cost = self.cache.get_cost(0, 1, 1, 1)

        self.assertEqual(self.cache._cache[(0, 1, 1, 1)], cost)
        self.assertEqual(self.cache._cache[(1, 1, 0, 1)], cost)

        self.cache._cache[(0, 1, 1, 1)] = cost + 1
        self.cache._cache[(1, 1, 0, 1)] = cost + 1

        self.assertEqual(self.cache._cache[(0, 1, 1, 1)], cost + 1)
        self.assertEqual(self.cache._cache[(1, 1, 0, 1)], cost + 1)


class RestorePathTests(utils_testcase.TestCase):

    def test(self):
        path_map = [[9, 9, 9, 9.0],
                    [9, 0, 1, 9.0],
                    [9, 9, 2, 2.3],
                    [9, 9, 3, 2.5],
                    [9, 5, 4, 9.0]]

        cells, cost = pathfinder._restore_path(from_x=1,
                                               from_y=1,
                                               to_x=1,
                                               to_y=4,
                                               path_map=path_map,
                                               width=4,
                                               height=5,
                                               travel_cost=SimpleRestoreTravelCost())
        self.assertEqual(cost, 5)
        self.assertEqual(cells, [(1, 1), (2, 1), (2, 2), (2, 3), (2, 4), (1, 4)])


class BuildPathMapTests(utils_testcase.TestCase):

    def test(self):
        cost_map = [[9, 9, 9, 9],
                    [2, 1, 1, 9],
                    [2, 2, 1, 9],
                    [2, 1, 1, 9],
                    [2, 3, 1, 9]]

        excluded_cells = {(2, 2), (1, 3)}

        path_map = pathfinder._build_path_map(from_x=1,
                                              from_y=1,
                                              to_x=1,
                                              to_y=4,
                                              width=4,
                                              height=5,
                                              travel_cost=SimpleTravelCost(map=cost_map),
                                              excluded_cells=excluded_cells)

        self.assertEqual(path_map,
                         [[7.0, 5.0,            6.0,            logic.MAX_COST],
                          [1.5, 0,              1.0,            6.0],
                          [3.5, 1.5,            logic.MAX_COST, logic.MAX_COST],
                          [5.5, logic.MAX_COST, logic.MAX_COST, logic.MAX_COST],
                          [7.5, 10.0,           logic.MAX_COST, logic.MAX_COST]])


class FindPathBetweenPlacesTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

    def test(self):
        cost_map = [[100 for x in range(map_conf.settings.WIDTH)]
                     for y in range(map_conf.settings.HEIGHT)]

        cost_map[1][2] = logic.MAX_COST
        cost_map[2][2] = logic.MAX_COST
        cost_map[1][3] = logic.MAX_COST
        cost_map[2][3] = logic.MAX_COST

        road_cells = set()

        for x, y in path.simple_path(from_x=self.place_1.x, from_y=self.place_1.y,
                                     to_x=self.place_3.x, to_y=self.place_3.y)._cells:
            cost_map[y][x] = 1
            road_cells.add((x, y))

        for x, y in path.simple_path(from_x=self.place_3.x, from_y=self.place_3.y,
                                     to_x=self.place_2.x, to_y=self.place_2.y)._cells:
            cost_map[y][x] = 1
            road_cells.add((x, y))

        for place in places_storage.places.all():
            road_cells.remove((place.x, place.y))

        travel_cost = SimpleTravelCost(map=cost_map)

        excluded_cells = [(self.place_3.x, self.place_3.y)]

        cells, cost = pathfinder.find_path_between_places(start_place=self.place_1,
                                                          finish_place=self.place_2,
                                                          travel_cost=travel_cost,
                                                          excluded_cells=excluded_cells)

        self.assertEqual(cost, 503)

        self.assertTrue(all(road_cell in cells for road_cell in road_cells))
        self.assertEqual(cells, [(1, 1), (1, 2), (0, 2), (0, 3), (0, 4), (1, 4), (2, 4), (2, 3), (3, 3)])
