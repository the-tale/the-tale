# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.game.logic import create_test_map

from .. import logic
from .. import relations



class LogicTests(testcase.TestCase):

    def setUp(self):
        super(LogicTests, self).setUp()
        create_test_map()

    def test_get_terrain_linguistics_restrictions(self):
        all_restrictions = set()
        for terrain in relations.TERRAIN.records:
            all_restrictions.add(logic.get_terrain_linguistics_restrictions(terrain))

        self.assertEqual(len(relations.TERRAIN.records), len(all_restrictions))
