# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.game.balance import constants as c
from the_tale.game.balance.power import Power, PowerDistribution, Damage


class PowerTest(testcase.TestCase):

    LEVELS = [1, 2, 3, 4, 5, 7, 11, 17, 19, 25, 30, 40, 60, 71, 82, 99, 101]

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



class DamageTest(testcase.TestCase):

    def test_total(self):
        self.assertEqual(Damage(100, 666).total, 766)

    def test_eq(self):
        self.assertEqual(Damage(100, 666), Damage(100, 666))
        self.assertNotEqual(Damage(101, 666), Damage(100, 666))
        self.assertNotEqual(Damage(100, 667), Damage(100, 666))

    def test_clone(self):
        self.assertEqual(Damage(100, 666).clone(), Damage(100, 666))

    def test_multiply(self):
        damage = Damage(100, 200)
        self.assertEqual(damage.multiply(0.5, 2), Damage(50, 400))
        self.assertEqual(damage, Damage(50, 400))

    def test_randomize(self):
        damages = set()

        damage = Damage(100, 100)

        for i in xrange(100000):
            test_damage = damage.clone()
            test_damage.randomize()
            damages.add((int(test_damage.physic), int(test_damage.magic)))

        test_damages = set()
        delta = int(100 * c.DAMAGE_DELTA)
        for physic in xrange(100-delta, 100+delta):
            for magic in xrange(100-delta, 100+delta):
                test_damages.add((physic, magic))

        self.assertEqual(damages, test_damages)

    def test_add(self):
        damage_1 = Damage(100, 150)
        damage_2 = Damage(200, 50)
        self.assertEqual(damage_1 + damage_2, Damage(300, 200))

        damage_1 += damage_2
        self.assertEqual(damage_1, Damage(300, 200))
        self.assertEqual(damage_2, Damage(200, 50))

    def test_mul(self):
        damage = Damage(100, 150)
        self.assertEqual(damage * 2, Damage(200, 300))

        damage *= 2
        self.assertEqual(damage, Damage(200, 300))

    def test_div(self):
        damage = Damage(100, 150)
        self.assertEqual(damage / 2, Damage(50, 75))

        damage /= 2
        self.assertEqual(damage, Damage(50, 75))
