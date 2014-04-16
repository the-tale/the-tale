# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.game.balance import constants as c
from the_tale.game.balance.power import Power, PowerDistribution


class PowerTest(testcase.TestCase):

    LEVELS = [1, 2, 3, 4, 5, 7, 11, 17, 19, 25, 30, 40, 60, 71, 82, 99, 101]

    # def test_expected_lvl_from_power(self):
    #     for level in self.LEVELS:
    #         print '------------'
    #         clean_power = Power.clean_power_for_hero_level(level)
    #         print clean_power
    #         power = Power.expected_power_to_level(level)
    #         print power
    #         print power + clean_power
    #         physic_level, magic_level = (power + clean_power + Power(1, 1)).expected_levels()
    #         print physic_level, magic_level
    #         self.assertEqual(level, physic_level)
    #         self.assertEqual(level, magic_level)

    #     physic_level, magic_level = Power(1, 1).expected_levels()
    #     self.assertTrue(physic_level < 1)
    #     self.assertTrue(magic_level < 1)

    #     self.assertEqual(Power(0, 0).expected_levels(), (0, 0))


    def check_better_artifact_power(self, distribution):
        median_power = Power.power_to_artifact(distribution, 100)

        for i in xrange(100):
            power = Power.better_artifact_power_randomized(distribution, 100)
            self.assertTrue(median_power.physic < power.physic)
            self.assertTrue(median_power.magic < power.magic)

    def test_better_artifact_power(self):
        self.check_better_artifact_power(distribution=PowerDistribution(0.5, 0.5))


    def test_better_artifact_power__physic(self):
        self.check_better_artifact_power(distribution=PowerDistribution(0.8, 0.2))


    def test_better_artifact_power__magic(self):
        self.check_better_artifact_power(distribution=PowerDistribution(0.2, 0.8))


    def test_better_artifact_power__on_low_levels(self):
        median_power = Power.power_to_artifact(PowerDistribution(0.5, 0.5), 1)

        self.assertEqual(median_power, Power(1, 1))

        powers = set()

        for i in xrange(100):
            power = Power.better_artifact_power_randomized(PowerDistribution(0.5, 0.5), 1)
            powers.add(power.magic)
            powers.add(power.physic)

        self.assertEqual(1 + c.ARTIFACT_BETTER_MIN_POWER_DELTA*2, len(powers))
