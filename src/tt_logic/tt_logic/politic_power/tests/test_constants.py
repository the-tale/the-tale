
import unittest

from .. import constants as c


class ConstantsTest(unittest.TestCase):

    def test_constants_values(self):

        self.assertEqual(c.POWER_PER_QUEST, 100)

        self.assertEqual(c.POWER_HISTORY_WEEKS, 6)
        self.assertEqual(c.POWER_HISTORY_LENGTH, 362880)

        self.assertEqual(c.POWER_RECALCULATE_STEPS, 1008)
        self.assertEqual(c.POWER_REDUCE_FRACTION, 0.9954417990588478)

        self.assertEqual(c.MODIFIER_HERO_ABILITIES, 3.0)

        self.assertEqual(c.EXPECTED_PLACE_FREEDOM_MAXIMUM, 1.0)

        self.assertEqual(c.MODIFIER_PLACE_FREEDOM, 1.5)
        self.assertEqual(c.MODIFIER_PERSON_BUILDING, 1.0)
        self.assertEqual(c.MODIFIER_HERO_COMPANION, 1.5)

        self.assertEqual(c.MODIFIER_PERSON_CHARACTER, 0.5)
        self.assertEqual(c.MODIFIER_HERO_ARTIFACTS_RARE, 0.2)
        self.assertEqual(c.MODIFIER_HERO_ARTIFACTS_EPIC, 0.6)

        self.assertEqual(c.MODIFIER_EMISSARY, 0.5)

        self.assertEqual(c.SOCIAL_CONNECTIONS_POWER_FRACTION, 0.1)

        self.assertEqual(c.EXPECTED_STABLE_BASE_QUEST_POWER, 600)
        self.assertEqual(c.EXPECTED_POWER_FROM_POLITIC, 6.1)

        self.assertEqual(c.MEDIUM_QUEST_POWER, 3660)

        self.assertEqual(c.CARD_MAX_POWER, 7200)

    def test_hero_power_fraction_is_big_enough(self):
        hero_bonus = c.MODIFIER_HERO_ABILITIES + c.MODIFIER_HERO_COMPANION + c.MODIFIER_HERO_ARTIFACTS_EPIC
        other_bonus = c.MODIFIER_PLACE_FREEDOM + c.MODIFIER_PERSON_BUILDING + c.MODIFIER_PERSON_CHARACTER + c.MODIFIER_EMISSARY

        self.assertAlmostEqual(hero_bonus / other_bonus, 1.457142857142857)
