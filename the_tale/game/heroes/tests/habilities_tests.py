# coding: utf-8

from django.test import TestCase

from game.actions.fake import FakeActor

from game.heroes.fake import FakeMessanger
from game.heroes.habilities import prototypes as common_abilities
from game.prototypes import TimePrototype


class HabilitiesTest(TestCase):

    def setUp(self):
        self.messanger = FakeMessanger()
        self.attacker = FakeActor(name='attacker')
        self.defender = FakeActor(name='defender')

    def tearDown(self):
        pass

    def test_hit(self):
        common_abilities.HIT.use(self.messanger, TimePrototype.get_current_time(), self.attacker, self.defender)
        self.assertTrue(self.defender.health < self.defender.max_health)
        self.assertEqual(self.messanger.messages, ['hero_ability_hit'])

    def test_magic_mushroom(self):
        common_abilities.MAGIC_MUSHROOM.use(self.messanger, TimePrototype.get_current_time(), self.attacker, self.defender)
        self.assertTrue(self.attacker.context.ability_magic_mushroom)
        self.assertFalse(self.defender.context.ability_magic_mushroom)
        self.assertEqual(self.messanger.messages, ['hero_ability_magicmushroom'])

    def test_sidestep(self):
        common_abilities.SIDESTEP.use(self.messanger, TimePrototype.get_current_time(), self.attacker, self.defender)
        self.assertFalse(self.attacker.context.ability_sidestep)
        self.assertTrue(self.defender.context.ability_sidestep)
        self.assertEqual(self.messanger.messages, ['hero_ability_sidestep'])

    def test_run_up_push(self):
        common_abilities.RUN_UP_PUSH.use(self.messanger, TimePrototype.get_current_time(), self.attacker, self.defender)
        self.assertFalse(self.attacker.context.stun_length)
        self.assertTrue(self.defender.context.stun_length)
        self.assertTrue(self.defender.health < self.defender.max_health)
        self.assertEqual(self.messanger.messages, ['hero_ability_runuppush'])

    def test_regeneration(self):
        self.attacker.healt = 1
        common_abilities.REGENERATION.use(self.messanger, TimePrototype.get_current_time(), self.attacker, self.defender)
        self.assertTrue(self.attacker.health > 1)
        self.assertEqual(self.messanger.messages, ['hero_ability_regeneration'])
