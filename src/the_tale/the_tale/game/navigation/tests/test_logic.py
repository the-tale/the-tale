

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
