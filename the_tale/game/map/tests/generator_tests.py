# coding: utf-8

from common.utils.testcase import TestCase

from game.map.generator.updater import roll_road


class GeneratorTests(TestCase):

    def setUp(self):
        pass

    def test_roll_road(self):
        self.assertEqual(roll_road(5, 4, 13, 8), 'rdrrdrrdrrdr')
        self.assertEqual(roll_road(13, 8, 5, 4), 'llullullullu')
        self.assertEqual(roll_road(5, 8, 13, 4), 'rrurrurrurru')
        self.assertEqual(roll_road(13, 4, 5, 8), 'ldlldlldlldl')

        self.assertEqual(roll_road(0, 4, 0, 8), 'dddd')
        self.assertEqual(roll_road(0, 8, 0, 4), 'uuuu')
        self.assertEqual(roll_road(5, 0, 13, 0), 'rrrrrrrr')
        self.assertEqual(roll_road(13, 0, 5, 0), 'llllllll')

        self.assertEqual(roll_road(5, 12, 3, 17), 'dlddldd')
