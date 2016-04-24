# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.game import politic_power
from the_tale.game.jobs import job


class FakePoliticPower(politic_power.PoliticPower):
    INNER_CIRCLE_SIZE = 2

    def job_effect_kwargs(self, owner):
        return {'actor_type': 'actor_type',
                'actor_name': 'actor_name',
                'person': None,
                'place': None,
                'positive_heroes': self._inner_positive_heroes,
                'negative_heroes': self._inner_negative_heroes,
                'job_power': 0.0 }


class FakeOwner(object):

    def __init__(self):
        self.job = job.Job(name='x', created_at_turn=0, effect=None, positive_power=0, negative_power=0, power_required=100000000)


class PoliticPowerTest(testcase.TestCase):

    def setUp(self):
        super(PoliticPowerTest, self).setUp()

        self.power = FakePoliticPower.create()
        self.owner = FakeOwner()


    def test_create(self):
        self.assertEqual(self.power.outer_power, 0)
        self.assertEqual(self.power.inner_power, 0)
        self.assertEqual(self.power.inner_circle, {})
        self.assertEqual(self.power._inner_positive_heroes, None)
        self.assertEqual(self.power._inner_negative_heroes, None)


    def test_serialization(self):
        self.assertEqual(self.power.serialize(), FakePoliticPower.deserialize(self.power.serialize()).serialize())


    def test_reset_cache(self):
        self.power._inner_positive_heroes = frozenset((1,))
        self.power._inner_negative_heroes = frozenset((2,))

        self.power.reset_cache()

        self.assertEqual(self.power._inner_positive_heroes, None)
        self.assertEqual(self.power._inner_negative_heroes, None)


    def test_change_power__without_hero(self):
        self.power.change_power(owner=self.owner, hero_id=None, has_in_preferences=False, power=1000)

        self.assertEqual(self.power.outer_power, 1000)
        self.assertEqual(self.power.inner_power, 0)
        self.assertEqual(self.power.inner_circle, {})
        self.assertEqual(self.power._inner_positive_heroes, None)
        self.assertEqual(self.power._inner_negative_heroes, None)


    def test_change_power__with_hero(self):
        self.power.change_power(owner=self.owner, hero_id=1, has_in_preferences=False, power=1000)

        self.assertEqual(self.power.outer_power, 1000)
        self.assertEqual(self.power.inner_power, 0)
        self.assertEqual(self.power.inner_circle, {})
        self.assertEqual(self.power._inner_positive_heroes, frozenset())
        self.assertEqual(self.power._inner_negative_heroes, frozenset())

        self.power.change_power(owner=self.owner, hero_id=2, has_in_preferences=True, power=2000)

        self.assertEqual(self.power.outer_power, 1000)
        self.assertEqual(self.power.inner_power, 2000)
        self.assertEqual(self.power.inner_circle, {2: 2000})
        self.assertEqual(self.power._inner_positive_heroes, frozenset((2, )))
        self.assertEqual(self.power._inner_negative_heroes, frozenset())


        self.power.change_power(owner=self.owner, hero_id=3, has_in_preferences=True, power=-3000)

        self.assertEqual(self.power.outer_power, 1000)
        self.assertEqual(self.power.inner_power, -1000)
        self.assertEqual(self.power.inner_circle, {2: 2000, 3: -3000})
        self.assertEqual(self.power._inner_positive_heroes, frozenset((2, )))
        self.assertEqual(self.power._inner_negative_heroes, frozenset((3, )))

        self.power.change_power(owner=self.owner, hero_id=4, has_in_preferences=True, power=4000)

        self.assertEqual(self.power.outer_power, 1000)
        self.assertEqual(self.power.inner_power, 3000)
        self.assertEqual(self.power.inner_circle, {2: 2000, 4: 4000, 3: -3000})
        self.assertEqual(self.power._inner_positive_heroes, frozenset((2, 4)))
        self.assertEqual(self.power._inner_negative_heroes, frozenset((3, )))

        self.power.change_power(owner=self.owner, hero_id=5, has_in_preferences=True, power=5000)

        self.assertEqual(self.power.outer_power, 1000)
        self.assertEqual(self.power.inner_power, 8000)
        self.assertEqual(self.power.inner_circle, {2: 2000, 4: 4000, 5: 5000, 3: -3000})
        self.assertEqual(self.power._inner_positive_heroes, frozenset((4, 5)))
        self.assertEqual(self.power._inner_negative_heroes, frozenset((3, )))


        self.power.change_power(owner=self.owner, hero_id=2, has_in_preferences=True, power=500)

        self.assertEqual(self.power.outer_power, 1500)
        self.assertEqual(self.power.inner_power, 8000)
        self.assertEqual(self.power.inner_circle, {2: 2500, 4: 4000, 5: 5000, 3: -3000})
        self.assertEqual(self.power._inner_positive_heroes, frozenset((4, 5)))
        self.assertEqual(self.power._inner_negative_heroes, frozenset((3, )))

        self.assertEqual(self.owner.job.positive_power, 11000)
        self.assertEqual(self.owner.job.negative_power, 3000)


    @mock.patch('the_tale.game.balance.constants.PLACE_POWER_REDUCE_FRACTION', 0.5)
    def test_sync_power(self):
        self.power._inner_positive_heroes = frozenset((1,))
        self.power._inner_negative_heroes = frozenset((2,))

        self.power.inner_circle = {1: 2, 2: 4, 3: 8}

        self.power.sync_power()
        self.assertEqual(self.power.inner_circle, {2: 2, 3: 4})

        self.power.sync_power()
        self.assertEqual(self.power.inner_circle, {3: 2})

        self.assertEqual(self.power._inner_positive_heroes, None)
        self.assertEqual(self.power._inner_negative_heroes, None)


    def test_inner_cyrcle(self):
        self.power.inner_circle = {1: 2, 2: 4, 3: 8, 4: -2, 5: -3, 6: -1}

        self.assertFalse(self.power.is_in_inner_circle(1))
        self.assertTrue(self.power.is_in_inner_circle(2))
        self.assertTrue(self.power.is_in_inner_circle(3))
        self.assertFalse(self.power.is_in_inner_circle(6))
        self.assertTrue(self.power.is_in_inner_circle(5))
        self.assertTrue(self.power.is_in_inner_circle(4))

        self.assertEqual(self.power._inner_positive_heroes, frozenset((2, 3)))
        self.assertEqual(self.power._inner_negative_heroes, frozenset((4, 5)))


    def test_total_politic_power_fraction(self):
        self.power.inner_power = 100
        self.power.outer_power = 200

        power_2 = FakePoliticPower.create()
        power_2.inner_power = 400
        power_2.outer_power = 200

        power_3 = FakePoliticPower.create()
        power_3.inner_power = 450
        power_3.outer_power = 450

        self.assertEqual(round(self.power.total_politic_power_fraction([self.power, power_2, power_3]), 2), 0.17)
        self.assertEqual(round(power_2.total_politic_power_fraction([self.power, power_2, power_3]), 2), 0.33)
        self.assertEqual(round(power_3.total_politic_power_fraction([self.power, power_2, power_3]), 2), 0.50)


    def test_total_politic_power_fraction__below_zero(self):
        self.power.inner_power = 100  # -> 500
        self.power.outer_power = -200 # -> 0

        power_2 = FakePoliticPower.create()
        power_2.inner_power = -400 # -> 0
        power_2.outer_power = 200  # -> 400

        power_3 = FakePoliticPower.create()
        power_3.inner_power = 450  # -> 850
        power_3.outer_power = 450  # -> 650

        self.assertEqual(round(self.power.total_politic_power_fraction([self.power, power_2, power_3]), 2), 0.19)
        self.assertEqual(round(power_2.total_politic_power_fraction([self.power, power_2, power_3]), 2), 0.19)
        self.assertEqual(round(power_3.total_politic_power_fraction([self.power, power_2, power_3]), 2), 0.62)
