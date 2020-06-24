
import unittest

from .. import constants as c
from .. import formulas as f


class FormulasTest(unittest.TestCase):

    def test_base_quest_power(self):
        self.assertEqual(f.base_quest_power(quest_rung=1), c.POWER_PER_QUEST)
        self.assertEqual(f.base_quest_power(quest_rung=10), c.POWER_PER_QUEST * 4.33)
        self.assertEqual(f.base_quest_power(quest_rung=25), c.POWER_PER_QUEST * 5.65)
        self.assertEqual(f.base_quest_power(quest_rung=50), c.POWER_PER_QUEST * 6.65)
        self.assertEqual(f.base_quest_power(quest_rung=75), c.POWER_PER_QUEST * 7.23)
        self.assertEqual(f.base_quest_power(quest_rung=100), c.POWER_PER_QUEST * 7.65)
        self.assertEqual(f.base_quest_power(quest_rung=200), c.POWER_PER_QUEST * 8.65)

    def test_expected_stable_base_quest_power(self):
        rung = 50
        rung_delta = 10
        delta = c.POWER_PER_QUEST

        self.assertAlmostEqual(f.base_quest_power(quest_rung=rung - rung_delta),
                               c.EXPECTED_STABLE_BASE_QUEST_POWER,
                               delta=delta)

        self.assertAlmostEqual(f.base_quest_power(quest_rung=rung + rung_delta),
                               c.EXPECTED_STABLE_BASE_QUEST_POWER,
                               delta=delta)

    def test_might_to_power(self):
        self.assertAlmostEqual(f.might_to_power(0), 0)
        self.assertAlmostEqual(f.might_to_power(10), 0.33, places=2)
        self.assertAlmostEqual(f.might_to_power(100), 0.67, places=2)
        self.assertAlmostEqual(f.might_to_power(1000), 1, places=2)
        self.assertAlmostEqual(f.might_to_power(10000), 1.33, places=2)
        self.assertAlmostEqual(f.might_to_power(100000), 1.67, places=2)

    def test_power_modifier_from_freedom(self):
        k = c.MODIFIER_PLACE_FREEDOM / c.EXPECTED_PLACE_FREEDOM_MAXIMUM

        self.assertAlmostEqual(f.power_modifier_from_freedom(-1.5), -1.5 * k)
        self.assertAlmostEqual(f.power_modifier_from_freedom(-1), -1.0 * k)
        self.assertAlmostEqual(f.power_modifier_from_freedom(-0.5), -0.5 * k)

        self.assertAlmostEqual(f.power_modifier_from_freedom(0), 0)

        self.assertAlmostEqual(f.power_modifier_from_freedom(0.5), 0.5 * k)
        self.assertAlmostEqual(f.power_modifier_from_freedom(1), 1.0 * k)
        self.assertAlmostEqual(f.power_modifier_from_freedom(1.5), 1.5 * k)
