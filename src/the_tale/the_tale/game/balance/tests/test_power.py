
import smart_imports

smart_imports.all()


class PowerTest(utils_testcase.TestCase):

    LEVELS = [1, 2, 3, 4, 5, 7, 11, 17, 19, 25, 30, 40, 60, 71, 82, 99, 101]

    def check_better_artifact_power(self, distribution):
        median_power = power.Power.power_to_artifact(distribution, 100)

        for i in range(100):
            artifact_power = power.Power.better_artifact_power_randomized(distribution, 100)
            self.assertTrue(median_power.physic < artifact_power.physic)
            self.assertTrue(median_power.magic < artifact_power.magic)

    def test_better_artifact_power(self):
        self.check_better_artifact_power(distribution=power.PowerDistribution(0.5, 0.5))

    def test_better_artifact_power__physic(self):
        self.check_better_artifact_power(distribution=power.PowerDistribution(0.8, 0.2))

    def test_better_artifact_power__magic(self):
        self.check_better_artifact_power(distribution=power.PowerDistribution(0.2, 0.8))

    def test_better_artifact_power__on_low_levels(self):
        median_power = power.Power.power_to_artifact(power.PowerDistribution(0.5, 0.5), 1)

        self.assertEqual(median_power, power.Power(1, 1))

        powers = set()

        for i in range(100):
            artifact_power = power.Power.better_artifact_power_randomized(power.PowerDistribution(0.5, 0.5), 1)
            powers.add(artifact_power.magic)
            powers.add(artifact_power.physic)

        self.assertEqual(1 + c.ARTIFACT_BETTER_MIN_POWER_DELTA * 2, len(powers))


class DamageTest(utils_testcase.TestCase):

    def test_total(self):
        self.assertEqual(power.Damage(100, 666).total, 766)

    def test_eq(self):
        self.assertEqual(power.Damage(100, 666), power.Damage(100, 666))
        self.assertNotEqual(power.Damage(101, 666), power.Damage(100, 666))
        self.assertNotEqual(power.Damage(100, 667), power.Damage(100, 666))

    def test_clone(self):
        self.assertEqual(power.Damage(100, 666).clone(), power.Damage(100, 666))

    def test_multiply(self):
        damage = power.Damage(100, 200)
        self.assertEqual(damage.multiply(0.5, 2), power.Damage(50, 400))
        self.assertEqual(damage, power.Damage(50, 400))

    def test_randomize(self):
        damages = set()

        damage = power.Damage(100, 100)

        for i in range(100000):
            test_damage = damage.clone()
            test_damage.randomize()
            damages.add((int(test_damage.physic), int(test_damage.magic)))

        test_damages = set()
        delta = int(100 * c.DAMAGE_DELTA)
        for physic in range(100 - delta, 100 + delta):
            for magic in range(100 - delta, 100 + delta):
                test_damages.add((physic, magic))

        self.assertEqual(damages, test_damages)

    def test_add(self):
        damage_1 = power.Damage(100, 150)
        damage_2 = power.Damage(200, 50)
        self.assertEqual(damage_1 + damage_2, power.Damage(300, 200))

        damage_1 += damage_2
        self.assertEqual(damage_1, power.Damage(300, 200))
        self.assertEqual(damage_2, power.Damage(200, 50))

    def test_mul(self):
        damage = power.Damage(100, 150)
        self.assertEqual(damage * 2, power.Damage(200, 300))

        damage *= 2
        self.assertEqual(damage, power.Damage(200, 300))

    def test_div(self):
        damage = power.Damage(100, 150)
        self.assertEqual(damage / 2, power.Damage(50, 75))

        damage /= 2
        self.assertEqual(damage, power.Damage(50, 75))
