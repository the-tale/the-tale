
import smart_imports

smart_imports.all()


class PopularityTests(utils_testcase.TestCase):

    def setUp(self):
        super(PopularityTests, self).setUp()

        self.popularity = objects.Popularity(places_fame={1: 100,
                                                          2: 300,
                                                          3: 200,
                                                          4: 200,
                                                          5: 400,
                                                          6: 50})

    def test_places_rating(self):
        self.assertEqual(self.popularity.places_rating(),
                         [(5, 400),
                          (2, 300),
                          (3, 200),
                          (4, 200),
                          (1, 100),
                          (6, 50)])

    def test_places_rating__no_records(self):
        self.assertEqual(objects.Popularity(places_fame={}).places_rating(), [])

    def test_get_allowed_places_ids__greate_number(self):
        self.assertEqual(self.popularity.get_allowed_places_ids(100, border=0),
                         {1, 2, 3, 4, 5, 6})

        self.assertEqual(self.popularity.get_allowed_places_ids(100, border=100),
                         {1, 2, 3, 4, 5})

        self.assertEqual(self.popularity.get_allowed_places_ids(100, border=240),
                         {2, 5})

    def test_get_allowed_places_ids__continue_to_equal_numbers(self):
        self.assertEqual(self.popularity.get_allowed_places_ids(3, border=0),
                         {5, 2, 3, 4})

        self.assertEqual(self.popularity.get_allowed_places_ids(3, border=200),
                         {5, 2, 3, 4})

        self.assertEqual(self.popularity.get_allowed_places_ids(3, border=250),
                         {5, 2})

    def test_get_allowed_places_ids(self):
        self.assertEqual(self.popularity.get_allowed_places_ids(2, border=0),
                         {5, 2})

    def test_get_allowed_places_ids__without_statistics(self):
        self.assertEqual(objects.Popularity(places_fame={}).get_allowed_places_ids(100, border=0), set())
