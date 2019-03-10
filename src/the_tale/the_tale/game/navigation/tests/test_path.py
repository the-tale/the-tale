
import smart_imports

smart_imports.all()


class SimplePathTests(utils_testcase.TestCase):

    def test_same_cell(self):
        test_path = path.simple_path(from_x=1, from_y=2, to_x=1, to_y=2)
        self.assertEqual(test_path._cells, [(1, 2)])

    def test_directions(self):
        test_path = path.simple_path(from_x=1, from_y=2, to_x=3, to_y=2)
        self.assertEqual(test_path._cells, [(1, 2), (2, 2), (3, 2)])

        test_path = path.simple_path(from_x=1, from_y=2, to_x=-3, to_y=2)
        self.assertEqual(test_path._cells, [(1, 2), (0, 2), (-1, 2), (-2, 2), (-3, 2)])

        test_path = path.simple_path(from_x=1, from_y=2, to_x=1, to_y=4)
        self.assertEqual(test_path._cells, [(1, 2), (1, 3), (1, 4)])

        test_path = path.simple_path(from_x=1, from_y=2, to_x=1, to_y=-2)
        self.assertEqual(test_path._cells, [(1, 2), (1, 1), (1, 0), (1, -1), (1, -2)])

    def test_incline(self):
        test_path = path.simple_path(from_x=1, from_y=-3, to_x=5, to_y=-1)
        self.assertEqual(test_path._cells, [(1, -3), (2, -3), (3, -3), (3, -2), (4, -2), (5, -2), (5, -1)])


class PathTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

    def test_initialization(self):
        test_path = path.Path(cells=[(1, 2), (1, 3), (2, 3)])

        self.assertEqual(test_path._cells, [(1, 2), (1, 3), (2, 3)])
        self.assertEqual(test_path._start_from, (1, 2))
        self.assertEqual(test_path._start_length, 0)
        self.assertEqual(test_path.length, 2)
        self.assertEqual(test_path._places_cache, None)

    def test_destination_coordinates(self):
        test_path = path.Path(cells=[(1, 2), (1, 3), (2, 3)])
        self.assertEqual(test_path.destination_coordinates(), (2, 3))

    def test_serialization(self):
        test_path = path.Path(cells=[(1, 2), (1, 3), (2, 3)])
        test_path.set_start(0.5, 1.5)

        self.assertEqual(test_path,
                         path.Path.deserialize(test_path.serialize()))

    def test_coordinates__simple_x(self):
        test_path = path.Path(cells=[(1, -3), (2, -3)])

        self.assertEqual(test_path.coordinates(0.0), (1, -3))
        self.assertEqual(test_path.coordinates(0.01), (1.01, -3))
        self.assertEqual(test_path.coordinates(0.25), (1.25, -3))
        self.assertEqual(test_path.coordinates(0.49), (1.49, -3))
        self.assertEqual(test_path.coordinates(0.50), (1.50, -3))
        self.assertEqual(test_path.coordinates(0.51), (1.51, -3))
        self.assertEqual(test_path.coordinates(0.75), (1.75, -3))
        self.assertEqual(test_path.coordinates(0.99), (1.99, -3))
        self.assertEqual(test_path.coordinates(1.0), (2, -3))

    def test_coordinates__simple_y(self):
        test_path = path.Path(cells=[(1, -3), (1, -2)])

        self.assertEqual(test_path.coordinates(0.0), (1, -3))
        self.assertEqual(test_path.coordinates(0.01), (1, -2.99))
        self.assertEqual(test_path.coordinates(0.25), (1, -2.75))
        self.assertEqual(test_path.coordinates(0.49), (1, -2.51))
        self.assertEqual(test_path.coordinates(0.50), (1, -2.50))
        self.assertEqual(test_path.coordinates(0.51), (1, -2.49))
        self.assertEqual(test_path.coordinates(0.75), (1, -2.25))
        self.assertEqual(test_path.coordinates(0.99), (1, -2.01))
        self.assertEqual(test_path.coordinates(1.0), (1, -2))

    def test_coordinates__simple_angle(self):
        test_path = path.Path(cells=[(1, -3), (1, -2), (0, -2)])

        self.assertEqual(test_path.coordinates(0.0), (1, -3))
        self.assertEqual(test_path.coordinates(0.01), (1, -2.98))
        self.assertEqual(test_path.coordinates(0.25), (1, -2.50))
        self.assertEqual(test_path.coordinates(0.49), (1, -2.02))
        self.assertEqual(test_path.coordinates(0.50), (1, -2))
        self.assertEqual(test_path.coordinates(0.51), (0.98, -2))
        self.assertEqual(test_path.coordinates(0.75), (0.50, -2))
        self.assertEqual(test_path.coordinates(0.99), (0.020000000000000018, -2))
        self.assertEqual(test_path.coordinates(1.0), (0, -2))

    def test_coordinates__minimal_path(self):
        test_path = path.Path(cells=[(1, -3)])

        for i in range(100):
            self.assertEqual(test_path.coordinates(i / 100), (1, -3))

    def test_append__duplicated_cell(self):
        path_1 = path.Path(cells=[(1, -3), (1, -2), (0, -2)])
        path_2 = path.Path(cells=[(0, -2), (0, -1), (0, 0)])

        path_1.append(path_2)

        self.assertEqual(path_1._cells, [(1, -3), (1, -2), (0, -2), (0, -1), (0, 0)])
        self.assertEqual(path_1.length, 4)

    def test_append__no_duplicated_cell(self):
        path_1 = path.Path(cells=[(1, -3), (1, -2), (0, -2)])
        path_2 = path.Path(cells=[(0, -1), (0, 0)])

        path_1.append(path_2)

        self.assertEqual(path_1._cells, [(1, -3), (1, -2), (0, -2), (0, -1), (0, 0)])
        self.assertEqual(path_1.length, 4)

    def test_append__concatenation_error(self):
        path_1 = path.Path(cells=[(1, -3), (1, -2), (0, -2)])
        path_2 = path.Path(cells=[(0, 0)])

        with self.assertRaises(ValueError):
            path_1.append(path_2)

    def get_places_path(self):
        path_0_1 = path.simple_path(from_x=0, from_y=0,
                                    to_x=self.place_1.x, to_y=self.place_1.y)
        path_1_2 = path.simple_path(from_x=self.place_1.x, from_y=self.place_1.y,
                                    to_x=self.place_2.x, to_y=self.place_2.y)
        path_2_3 = path.simple_path(from_x=self.place_2.x, from_y=self.place_2.y,
                                    to_x=self.place_3.x, to_y=self.place_3.y)

        test_path = path_0_1
        test_path.append(path_1_2)
        test_path.append(path_2_3)

        return test_path

    def test_places_positions(self):
        path = self.get_places_path()
        self.assertEqual(path._places_positions(), [(0.25, self.place_1.id),
                                                    (0.75, self.place_2.id),
                                                    (1.00, self.place_3.id)])

    def test_places_positions__no_places(self):
        self.assertNotIn((2, 2), {(place.x, place.y) for place in places_storage.places.all()})
        self.assertNotIn((2, 3), {(place.x, place.y) for place in places_storage.places.all()})

        test_path = path.Path(cells=[(2, 2), (2, 3)])

        self.assertEqual(test_path._places_positions(), [])

    def test_places_positions__no_places__minimum_length(self):
        self.assertNotIn((2, 2), {(place.x, place.y) for place in places_storage.places.all()})

        test_path = path.Path(cells=[(2, 2)])

        self.assertEqual(test_path._places_positions(), [])

    def test_places_positions__has_places__minimum_length(self):
        test_path = path.Path(cells=[(self.place_1.x, self.place_1.y)])

        self.assertEqual(test_path._places_positions(), [(0, self.place_1.id)])

    def test_next_place_at(self):
        test_path = self.get_places_path()

        self.assertEqual(test_path.next_place_at(0.00), (0.25, self.place_1.id))
        self.assertEqual(test_path.next_place_at(0.24), (0.25, self.place_1.id))
        self.assertEqual(test_path.next_place_at(0.25), (0.75, self.place_2.id))
        self.assertEqual(test_path.next_place_at(0.26), (0.75, self.place_2.id))
        self.assertEqual(test_path.next_place_at(0.74), (0.75, self.place_2.id))
        self.assertEqual(test_path.next_place_at(0.75), (1.00, self.place_3.id))
        self.assertEqual(test_path.next_place_at(0.76), (1.00, self.place_3.id))
        self.assertEqual(test_path.next_place_at(0.99), (1.00, self.place_3.id))
        self.assertEqual(test_path.next_place_at(1.00), (None, None))

    def test_set_start(self):
        test_path = path.Path(cells=[(1, 2), (1, 3), (2, 3)])
        test_path.set_start(0.5, 0.5)

        self.assertEqual(test_path._cells, [(1, 2), (1, 3), (2, 3)])
        self.assertEqual(test_path._start_from, (0.5, 0.5))
        self.assertEqual(test_path._start_length, logic.euclidean_distance(0.5, 0.5, 1, 2))
        self.assertEqual(test_path.length, 2 + test_path._start_length)
        self.assertEqual(test_path._places_cache, None)

    def test_set_start__skip_first_cell(self):
        test_path = path.Path(cells=[(1, 2), (1, 3), (2, 3)])
        test_path.set_start(1.0, 2.1)

        self.assertEqual(test_path._cells, [(1, 3), (2, 3)])
        self.assertEqual(test_path._start_from, (1, 2.1))
        self.assertEqual(test_path._start_length, logic.euclidean_distance(1.0, 2.1, 1, 3))
        self.assertEqual(test_path.length, 1 + test_path._start_length)
        self.assertEqual(test_path._places_cache, None)

    def test_append__after_set_start(self):
        test_path = path.Path(cells=[(1, 2), (1, 3), (2, 3)])
        test_path.set_start(0.5, 0.5)
        test_path.append(path.Path(cells=[(2, 3), (2, 4), (2, 5)]))

        self.assertEqual(test_path._cells, [(1, 2), (1, 3), (2, 3), (2, 4), (2, 5)])
        self.assertEqual(test_path._start_from, (0.5, 0.5))
        self.assertEqual(test_path._start_length, logic.euclidean_distance(0.5, 0.5, 1, 2))
        self.assertEqual(test_path.length, 4 + test_path._start_length)
        self.assertEqual(test_path._places_cache, None)

    def test_places_positions__after_set_start(self):
        path = self.get_places_path()
        path.set_start(-2, 0)
        self.assertEqual(path._places_positions(), [(0.4, self.place_1.id),
                                                    (0.8, self.place_2.id),
                                                    (1.00, self.place_3.id)])

    def test_places_positions__no_places__after_set_start(self):
        self.assertNotIn((2, 2), {(place.x, place.y) for place in places_storage.places.all()})
        self.assertNotIn((2, 3), {(place.x, place.y) for place in places_storage.places.all()})

        test_path = path.Path(cells=[(2, 2), (2, 3)])
        test_path.set_start(1.75, 1.75)

        self.assertEqual(test_path._places_positions(), [])

    def test_places_positions__no_places__minimum_length__after_set_start(self):
        self.assertNotIn((2, 2), {(place.x, place.y) for place in places_storage.places.all()})

        test_path = path.Path(cells=[(2, 2)])
        test_path.set_start(1.75, 1.75)

        self.assertEqual(test_path._places_positions(), [])

    def test_places_positions__has_places__minimum_length__after_set_start(self):
        test_path = path.Path(cells=[(self.place_1.x, self.place_1.y)])
        test_path.set_start(self.place_1.x - 0.3, self.place_1.y)

        self.assertEqual(test_path._places_positions(), [(1.0, self.place_1.id)])

    def test_coordinates__set_start(self):
        test_path = path.Path(cells=[(1, -3), (1, -2), (0, -2)])
        test_path.set_start(0.5, -3)

        self.assertEqual(test_path.coordinates(0.00), (0.5, -3))
        self.assertEqual(test_path.coordinates(0.01), (0.525, -3))
        self.assertEqual(test_path.coordinates(0.10), (0.75, -3))
        self.assertEqual(test_path.coordinates(0.19), (0.975, -3))
        self.assertEqual(test_path.coordinates(0.20), (1, -3))
        self.assertEqual(test_path.coordinates(0.21), (1, -2.975))
        self.assertEqual(test_path.coordinates(0.30), (1, -2.75))
        self.assertEqual(test_path.coordinates(0.40), (1, -2.5))
        self.assertEqual(test_path.coordinates(0.59), (1, -2.0250000000000004))
        self.assertEqual(test_path.coordinates(0.60), (1, -2))
        self.assertEqual(test_path.coordinates(0.61), (0.9750000000000001, -2))
        self.assertEqual(test_path.coordinates(0.80), (0.4999999999999998, -2))
        self.assertEqual(test_path.coordinates(0.99), (0.02499999999999991, -2))
        self.assertEqual(test_path.coordinates(1.00), (0, -2))

    def test_coordinates__minimal_path__set_start(self):
        test_path = path.Path(cells=[(1, -3)])
        test_path.set_start(0.5, -3)

        self.assertEqual(test_path.coordinates(0.00), (0.5, -3))
        self.assertEqual(test_path.coordinates(0.50), (0.75, -3))
        self.assertEqual(test_path.coordinates(1.00), (1, -3))
