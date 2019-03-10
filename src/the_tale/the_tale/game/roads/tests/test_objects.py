
import smart_imports

smart_imports.all()


class RoadTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.road = logic.road_between_places(self.place_1, self.place_2)
        self.expected_cells = [(1, 1),
                               (2, 1),
                               (2, 2),
                               (3, 2),
                               (3, 3)]

    def test_get_cells(self):
        self.assertEqual(set(self.road.get_cells()),
                         set(self.expected_cells))

    def test_get_stabilization_price_for(self):
        self.place_1.attrs.politic_radius = 2
        self.place_2.attrs.politic_radius = 2

        price_1 = self.road.get_stabilization_price_for(self.place_1)
        price_2 = self.road.get_stabilization_price_for(self.place_2)

        expected_total_price = logic.road_support_cost(cells=self.expected_cells[1:-1])

        self.assertTrue(price_1 > 0)
        self.assertTrue(price_2 > 0)
        self.assertAlmostEqual(price_1 + price_2, expected_total_price)
