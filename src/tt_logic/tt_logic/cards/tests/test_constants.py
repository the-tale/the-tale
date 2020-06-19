
import unittest

from .. import constants


class ConstantsTest(unittest.TestCase):

    def test_constants_values(self):
        self.assertEqual(constants.NORMAL_RECEIVE_TIME, 6)
        self.assertEqual(constants.RECEIVE_TIME, 6*60*60)
        self.assertEqual(constants.LEVEL_MULTIPLIERS, [1, 3.5, 12, 42, 150])

        self.assertEqual(constants.NORMAL_PLAYER_SPEED, 1.0)
        self.assertEqual(constants.PREMIUM_PLAYER_SPEED, 1.5)
