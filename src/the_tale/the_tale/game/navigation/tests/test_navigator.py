
import smart_imports

smart_imports.all()


class AllowedPlacesPairsTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

    def test_roads_condition(self):
        pairs = list(navigator.allowed_places_pairs(max_distance_between_places=0))

        self.assertEqual(pairs,
                         [(self.place_1, self.place_2),
                          (self.place_2, self.place_3)])

    def test_distance_condition(self):
        pairs = list(navigator.allowed_places_pairs(max_distance_between_places=1000))

        self.assertEqual(pairs,
                         [(self.place_1, self.place_2),
                          (self.place_1, self.place_3),
                          (self.place_2, self.place_3)])


class BuildPathsTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

    def test_success(self):
        travel_cost = navigation_pathfinder.TravelCost(map=map_storage.cells.get_map(),
                                                       expected_battle_complexity=1.0)
        paths = navigator.build_paths(travel_cost,
                                      places_pairs=[(self.place_1, self.place_2),
                                                    (self.place_1, self.place_3)])

        self.assertEqual(set(paths.keys()),
                         {(self.place_1.id, self.place_2.id),
                          (self.place_1.id, self.place_3.id),
                          (self.place_2.id, self.place_1.id),
                          (self.place_3.id, self.place_1.id)})

        self.assertEqual(paths[(self.place_1.id, self.place_2.id)][1], paths[(self.place_2.id, self.place_1.id)][1])
        self.assertEqual(paths[(self.place_1.id, self.place_3.id)][1], paths[(self.place_3.id, self.place_1.id)][1])

        self.assertEqual(paths[(self.place_1.id, self.place_2.id)][0], tuple(reversed(paths[(self.place_2.id, self.place_1.id)][0])))
        self.assertEqual(paths[(self.place_1.id, self.place_3.id)][0], tuple(reversed(paths[(self.place_3.id, self.place_1.id)][0])))

    def test_start_and_end(self):
        travel_cost = navigation_pathfinder.TravelCost(map=map_storage.cells.get_map(),
                                                       expected_battle_complexity=1.0)
        paths = navigator.build_paths(travel_cost,
                                      places_pairs=[(self.place_1, self.place_2),
                                                    (self.place_1, self.place_3),
                                                    (self.place_2, self.place_3)])

        for start_place in places_storage.places.all():
            for end_place in places_storage.places.all():
                if start_place.id == end_place.id:
                    continue

                cells, cost = paths[(start_place.id, end_place.id)]

                self.assertEqual(cells[0], (start_place.x, start_place.y))
                self.assertEqual(cells[-1], (end_place.x, end_place.y))


class GetPathBetweenPlacesTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.paths = {(self.place_1.id, self.place_2.id): ([(0, 1), (1, 1)], 100),
                      (self.place_2.id, self.place_3.id): ([(1, 1), (2, 1), (2, 2)], 150),
                      (self.place_1.id, self.place_3.id): ([(0, 1), (1, 1), (1, 2), (2, 2)], 300)}

        for key, (cells, cost) in list(self.paths.items()):
            self.paths[(key[1], key[0])] = (list(reversed(cells)), cost)

    def test_one_step(self):
        test_path, cost = navigator.get_path_between_places(from_place_id=self.place_1.id,
                                                            to_place_id=self.place_2.id,
                                                            paths=self.paths,
                                                            cost_modifiers={place.id: 0 for place in places_storage.places.all()})
        self.assertEqual(test_path, path.Path(cells=[(0, 1), (1, 1)]))
        self.assertEqual(cost, 100)

    def test_multiple_steps(self):
        test_path, cost = navigator.get_path_between_places(from_place_id=self.place_1.id,
                                                            to_place_id=self.place_3.id,
                                                            paths=self.paths,
                                                            cost_modifiers={place.id: 0 for place in places_storage.places.all()})
        self.assertEqual(test_path, path.Path(cells=[(0, 1), (1, 1), (2, 1), (2, 2)]))
        self.assertEqual(cost, 250)

    def test_start_and_end(self):
        navigator_object = map_storage.cells._navigators[heroes_relations.RISK_LEVEL.NORMAL]

        for start_place in places_storage.places.all():
            for end_place in places_storage.places.all():
                test_path, cost = navigator_object.get_path_between_places(from_place_id=start_place.id,
                                                                           to_place_id=end_place.id,
                                                                           cost_modifiers={place.id: 0
                                                                                           for place in places_storage.places.all()})
                self.assertEqual(test_path._cells[0], (start_place.x, start_place.y))
                self.assertEqual(test_path._cells[-1], (end_place.x, end_place.y))


class BuildPathToPlaceTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.navigator = map_storage.cells._navigators[heroes_relations.RISK_LEVEL.NORMAL]

    def test_from_place(self):
        test_path = self.navigator.build_path_to_place(from_x=self.place_1.x,
                                                       from_y=self.place_1.y,
                                                       to_place_id=self.place_2.id,
                                                       cost_modifiers={place.id: 0 for place in places_storage.places.all()})

        self.assertEqual((self.place_1.x, self.place_1.y), test_path._cells[0])
        self.assertEqual((self.place_2.x, self.place_2.y), test_path._cells[-1])

        test_path = self.navigator.build_path_to_place(from_x=self.place_1.x,
                                                       from_y=self.place_1.y,
                                                       to_place_id=self.place_3.id,
                                                       cost_modifiers={place.id: 0 for place in places_storage.places.all()})

        self.assertEqual((self.place_1.x, self.place_1.y), test_path._cells[0])
        self.assertEqual((self.place_3.x, self.place_3.y), test_path._cells[-1])

    def test_choose_main_path(self):
        x = self.place_1.x - 1
        y = self.place_1.y - 1

        self.assertEqual(map_storage.cells(x, y).nearest_place_id, self.place_1.id)

        main_path = self.navigator.build_path_to_place(from_x=self.place_1.x,
                                                       from_y=self.place_1.y,
                                                       to_place_id=self.place_2.id,
                                                       cost_modifiers={place.id: 0 for place in places_storage.places.all()})

        test_path = self.navigator.build_path_to_place(from_x=x,
                                                       from_y=y,
                                                       to_place_id=self.place_2.id,
                                                       cost_modifiers={place.id: 0 for place in places_storage.places.all()})

        self.assertEqual(test_path._cells[-len(main_path._cells):], main_path._cells)

        self.assertEqual((self.place_1.x, self.place_1.y), test_path._cells[2])
        self.assertEqual((self.place_2.x, self.place_2.y), test_path._cells[-1])

    def test_choose_alternative_path(self):
        x = self.place_1.x + 1
        y = self.place_1.y + 1

        map_storage.cells(x, y).nearest_place_id = self.place_1.id

        main_path = self.navigator.build_path_to_place(from_x=self.place_1.x,
                                                       from_y=self.place_1.y,
                                                       to_place_id=self.place_2.id,
                                                       cost_modifiers={place.id: 0 for place in places_storage.places.all()})

        test_path = self.navigator.build_path_to_place(from_x=x,
                                                       from_y=y,
                                                       to_place_id=self.place_2.id,
                                                       cost_modifiers={place.id: 0 for place in places_storage.places.all()})

        self.assertNotIn((self.place_1.x, self.place_1.y), test_path._cells)
        self.assertEqual((self.place_2.x, self.place_2.y), test_path._cells[-1])


class NavigatorTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.navigators = map_storage.cells._navigators

    def test_initialization_and_sync(self):
        for navigator in self.navigators.values():
            self.assertNotEqual(navigator._paths, None)
            self.assertNotEqual(navigator._travel_cost, None)
