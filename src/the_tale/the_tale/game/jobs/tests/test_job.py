# coding: utf-8

import random

from unittest import mock

from the_tale.common.utils import testcase

from the_tale.linguistics import logic as linguistics_logic

from the_tale.game.jobs import job
from the_tale.game.jobs import effects


class FakeJob(job.Job):
    ACTOR = random.choice(('person', 'place'))


class JobTest(testcase.TestCase):

    @mock.patch('the_tale.game.prototypes.TimePrototype.get_current_turn_number', classmethod(lambda cls: 666))
    def setUp(self):
        super(JobTest, self).setUp()
        linguistics_logic.sync_static_restrictions()
        self.job = FakeJob.create(normal_power=1000)


    def test_create(self):
        self.assertEqual(self.job.created_at_turn, 666)
        self.assertEqual(self.job.positive_power, 0)
        self.assertEqual(self.job.negative_power, 0)
        self.assertEqual(self.job.power_required, 1000 * self.job.effect.power_modifier)
        self.assertTrue(self.job.effect.group.is_ON_HEROES)


    @mock.patch('the_tale.game.prototypes.TimePrototype.get_current_turn_number', classmethod(lambda cls: 777))
    def test_new_job__negative_power_reset(self):
        self.job.positive_power = 1
        self.job.negative_power = 2

        effect = effects.EFFECT.random()
        self.job.new_job(effect=effect, normal_power=2500)

        self.assertEqual(self.job.created_at_turn, 777)
        self.assertEqual(self.job.positive_power, 1)
        self.assertEqual(self.job.negative_power, 0)
        self.assertEqual(self.job.power_required, 2500*self.job.effect.power_modifier)
        self.assertEqual(self.job.effect, effect)


    @mock.patch('the_tale.game.prototypes.TimePrototype.get_current_turn_number', classmethod(lambda cls: 777))
    def test_new_job__positive_power_reset(self):
        self.job.positive_power = 2
        self.job.negative_power = 1

        effect = effects.EFFECT.random()
        self.job.new_job(effect=effect, normal_power=2500)

        self.assertEqual(self.job.created_at_turn, 777)
        self.assertEqual(self.job.positive_power, 0)
        self.assertEqual(self.job.negative_power, 1)
        self.assertEqual(self.job.power_required, 2500*self.job.effect.power_modifier)
        self.assertEqual(self.job.effect, effect)


    def test_serialization(self):
        self.assertEqual(self.job.serialize(), FakeJob.deserialize(self.job.serialize()).serialize())


    def test_give_power(self):
        self.job.power_required = 1000

        self.job.give_power(100)
        self.assertFalse(self.job.is_completed())
        self.assertEqual(self.job.get_apply_effect_method(), None)

        self.job.give_power(899)
        self.assertFalse(self.job.is_completed())
        self.assertEqual(self.job.get_apply_effect_method(), None)

        self.job.give_power(-999)
        self.assertFalse(self.job.is_completed())
        self.assertEqual(self.job.get_apply_effect_method(), None)

        self.job.give_power(1)
        self.assertTrue(self.job.is_completed())
        self.assertNotEqual(self.job.get_apply_effect_method(), None)

        self.assertEqual(self.job.positive_power, 1000)
        self.assertEqual(self.job.negative_power, 999)
