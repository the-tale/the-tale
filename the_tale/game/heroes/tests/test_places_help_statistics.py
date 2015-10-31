# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.game.heroes.places_help_statistics import PlacesHelpStatistics
from the_tale.game.heroes.conf import heroes_settings


class PlacesHelpStatisticsTests(testcase.TestCase):

    def setUp(self):
        super(PlacesHelpStatisticsTests, self).setUp()

        self.statistics = PlacesHelpStatistics()

    def fill_statistics(self):
        self.statistics.add_place(5)
        self.statistics.add_place(1)
        self.statistics.add_place(2)
        self.statistics.add_place(4)
        self.statistics.add_place(4)
        self.statistics.add_place(1)
        self.statistics.add_place(4)

    def test_initialization(self):
        self.assertFalse(self.statistics.updated)
        self.assertEqual(self.statistics.history, [])

    def test_serialization(self):
        self.statistics.add_place(1)
        self.statistics.add_place(2)
        self.statistics.add_place(1)

        self.assertEqual(self.statistics.serialize(),
                         PlacesHelpStatistics.deserialize(self.statistics.serialize()).serialize())


    def test_add_place(self):
        self.assertFalse(self.statistics.updated)
        self.statistics.add_place(1)
        self.assertTrue(self.statistics.updated)
        self.statistics.add_place(1)
        self.assertEqual(len(self.statistics.history), 2)

    def test_add_place__overgrowth(self):
        for i in xrange(0, heroes_settings.PLACE_HELP_HISTORY_SIZE):
            self.statistics.add_place(i)
        self.statistics.add_place(666)
        self.assertEqual(self.statistics.history, range(1, heroes_settings.PLACE_HELP_HISTORY_SIZE) + [666])

    def test_get_most_common_places(self):
        self.fill_statistics()

        self.assertEqual(self.statistics._get_most_common_places(),
                         [(4, 3), (1, 2), (2, 1), (5, 1)])

    def test_get_allowed_places_ids__greate_number(self):
        self.fill_statistics()
        self.assertEqual(self.statistics.get_allowed_places_ids(100),
                         [4, 1, 2, 5])

    def test_get_allowed_places_ids__continue_to_equal_numbers(self):
        self.fill_statistics()
        self.assertEqual(self.statistics.get_allowed_places_ids(3),
                         [4, 1, 2, 5])

    def test_get_allowed_places_ids(self):
        self.fill_statistics()
        self.assertEqual(self.statistics.get_allowed_places_ids(2),
                         [4, 1])

    def test_get_allowed_places_ids__without_statistics(self):
        self.assertEqual(self.statistics.get_allowed_places_ids(1), [])
