

import smart_imports

smart_imports.all()


class NormalisePathTests(utils_testcase.TestCase):

    def test_empty_path(self):
        self.assertEqual(logic.normalise_path([]), [])

    def test_single_cell(self):
        self.assertEqual(logic.normalise_path([(1, 2)]), [(1, 2)])

    def test_multiple_cell(self):
        self.assertEqual(logic.normalise_path([(1, 2), (1, 3), (2, 3)]), [(1, 2), (1, 3), (2, 3)])

    def test_cycle_from_start(self):
        self.assertEqual(logic.normalise_path([(1, 2), (1, 3), (2, 3), (2, 2), (1, 2), (1, 1), (0, 1)]),
                         [(1, 2), (1, 1), (0, 1)])

    def test_cycle_from_end(self):
        self.assertEqual(logic.normalise_path([(0, 1), (1, 1), (1, 2), (1, 3), (2, 3), (2, 2), (1, 2)]),
                         [(0, 1), (1, 1), (1, 2)])

    def test_cycle_in_middle(self):
        self.assertEqual(logic.normalise_path([(0, 1), (1, 1), (1, 2), (1, 3), (2, 3), (2, 2), (1, 2), (2, 2), (3, 2), (3, 3)]),
                         [(0, 1), (1, 1), (1, 2), (2, 2), (3, 2), (3, 3)])

    def test_multiple_cycles(self):
        self.assertEqual(logic.normalise_path([(0, 1), (1, 1), (2, 1), (3, 1), (3, 0), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
                                               (3, 4), (3, 3), (2, 3), (1, 3), (0, 3)]),
                         [(0, 1), (1, 1), (2, 1), (2, 2), (2, 3), (1, 3), (0, 3)])

    def test_full_cylce(self):
        self.assertEqual(logic.normalise_path([(0, 1), (1, 1), (2, 1), (3, 1), (3, 2), (2, 2), (1, 2), (0, 2), (0, 1)]),
                         [(0, 1)])


class NearestPointOnSectionTests(utils_testcase.TestCase):

    def test_point_1(self):
        distance, percents, x, y = logic.nearest_point_on_section(1.0, 2.0,
                                                                  1.0, 2.0,
                                                                  7.0, 5.0)

        self.assertEqual(distance, 0)
        self.assertEqual(percents, 0)
        self.assertEqual((x, y), (1.0, 2.0))

    def test_point_2(self):
        distance, percents, x, y = logic.nearest_point_on_section(7.0, 5.0,
                                                                  1.0, 2.0,
                                                                  7.0, 5.0)

        self.assertEqual(distance, 0)
        self.assertEqual(percents, 1)
        self.assertEqual((x, y), (7.0, 5.0))

    def test_on_line_before_point_1(self):
        distance, percents, x, y = logic.nearest_point_on_section(-1.0, 1.0,
                                                                  1.0, 2.0,
                                                                  7.0, 5.0)

        self.assertEqual(distance, math.sqrt(1**2 + 2**2))
        self.assertEqual(percents, 0)
        self.assertEqual((x, y), (1.0, 2.0))

    def test_on_line_after_point_2(self):
        distance, percents, x, y = logic.nearest_point_on_section(9.0, 6.0,
                                                                  1.0, 2.0,
                                                                  7.0, 5.0)

        self.assertEqual(distance, math.sqrt(1**2 + 2**2))
        self.assertEqual(percents, 1)
        self.assertEqual((x, y), (7.0, 5.0))

    def test_on_line_between_points(self):
        distance, percents, x, y = logic.nearest_point_on_section(5.0, 4.0,
                                                                  1.0, 2.0,
                                                                  7.0, 5.0)

        self.assertEqual(distance, 0)
        self.assertEqual(percents, 2 / 3)
        self.assertEqual((x, y), (5.0, 4.0))

    def test_not_on_line_before_point_1(self):
        distance, percents, x, y = logic.nearest_point_on_section(0.0, -1.0,
                                                                  1.0, 2.0,
                                                                  7.0, 5.0)

        self.assertEqual(distance, logic.euclidean_distance(0.0, -1.0, 1.0, 2.0))
        self.assertEqual(percents, 0)
        self.assertEqual((x, y), (1.0, 2.0))

    def test_not_on_line_after_point_2(self):
        distance, percents, x, y = logic.nearest_point_on_section(8.0, 8.0,
                                                                  1.0, 2.0,
                                                                  7.0, 5.0)

        self.assertEqual(distance, logic.euclidean_distance(8.0, 8.0, 7.0, 5.0))
        self.assertEqual(percents, 1.0)
        self.assertEqual((x, y), (7.0, 5.0))

    def test_not_on_line_between_points(self):
        distance, percents, x, y = logic.nearest_point_on_section(6.0, 2.0,
                                                                  1.0, 2.0,
                                                                  7.0, 5.0)

        self.assertEqual(distance, math.sqrt(1**2 + 2**2))
        self.assertEqual(percents, 2 / 3)
        self.assertEqual((x, y), (5.0, 4.0))

    def test_vertical(self):
        distance, percents, x, y = logic.nearest_point_on_section(5.0, 2.5,
                                                                  4.0, 3.0,
                                                                  4.0, 2.0)

        self.assertEqual(distance, 1.0)
        self.assertAlmostEqual(percents, 0.5)
        self.assertEqual((x, y), (4.0, 2.5))
