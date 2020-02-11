
import smart_imports

smart_imports.all()


class InnerCircleTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        self.rating = [(1, 100),
                       (2, 200),
                       (3, -300),
                       (4, 0),
                       (5, 400),
                       (6, 500),
                       (7, -100),
                       (8, -200)]

        self.circle = objects.InnerCircle(rating=self.rating, size=5)

    def test_initialize(self):
        self.assertEqual(self.circle.size, 5)
        self.assertEqual(self.circle.rating, [(6, 500),
                                              (5, 400),
                                              (3, -300),
                                              (2, 200),
                                              (8, -200),
                                              (1, 100),
                                              (7, -100),
                                              (4, 0)])
        self.assertEqual(self.circle.powers, dict(self.rating))
        self.assertEqual(self.circle.circle, {6, 5, 3, 2, 8})
        self.assertEqual(self.circle.total_positive_heroes_number, 4)
        self.assertEqual(self.circle.total_negative_heroes_number, 3)
        self.assertEqual(self.circle.circle_positive_heroes_number, 3)
        self.assertEqual(self.circle.circle_negative_heroes_number, 2)

    def test_initialize__empty_circle(self):
        circle = objects.InnerCircle(rating=[], size=2)

        self.assertEqual(circle.size, 2)
        self.assertEqual(circle.rating, [])
        self.assertEqual(circle.powers, {})
        self.assertEqual(circle.circle, frozenset())
        self.assertEqual(circle.total_positive_heroes_number, 0)
        self.assertEqual(circle.total_negative_heroes_number, 0)
        self.assertEqual(circle.circle_positive_heroes_number, 0)
        self.assertEqual(circle.circle_negative_heroes_number, 0)

    def test_in_circle(self):
        self.assertFalse(self.circle.in_circle(1))
        self.assertTrue(self.circle.in_circle(2))
        self.assertTrue(self.circle.in_circle(3))
        self.assertFalse(self.circle.in_circle(4))
        self.assertTrue(self.circle.in_circle(5))
        self.assertTrue(self.circle.in_circle(6))
        self.assertFalse(self.circle.in_circle(7))
        self.assertTrue(self.circle.in_circle(8))

    def test_heroes_ids(self):
        self.assertCountEqual(self.circle.heroes_ids(), [1, 2, 3, 4, 5, 6, 7, 8])

    def test_ui_info(self):
        self.assertEqual(self.circle.ui_info(),
                         {'size': 5,
                          'rating': [(6, 500),
                                     (5, 400),
                                     (3, -300),
                                     (2, 200),
                                     (8, -200),
                                     (1, 100),
                                     (7, -100),
                                     (4, 0)]})
