
import unittest

from .. import constants


class ConstantsTest(unittest.TestCase):

    def test_constants_values(self):
        self.assertEqual(constants.INACTIVE_PREMIUM_LIVETIME, 365*24*60*60)
