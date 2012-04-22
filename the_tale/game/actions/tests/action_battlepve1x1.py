# coding: utf-8

from django.test import TestCase

from game.heroes.logic import create_mob_for_hero
from game.logic import create_test_bundle, create_test_map
from game.actions.prototypes import ActionBattlePvE1x1Prototype

class BattlePvE1x1ActionTest(TestCase):

    def setUp(self):
        create_test_map()

        self.bundle = create_test_bundle('BattlePvE1x1ActionTest')
        self.hero = self.bundle.tests_get_hero()

        self.action_idl = self.bundle.tests_get_last_action()
        self.bundle.add_action(ActionBattlePvE1x1Prototype.create(self.action_idl, mob=create_mob_for_hero(self.hero)))
        self.action_battle = self.bundle.tests_get_last_action()


    def tearDown(self):
        pass


    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_battle.leader, True)


    def test_mob_killed(self):
        self.action_battle.mob.health = 0
        self.bundle.process_turn(1)
        self.assertEqual(len(self.bundle.actions), 1)
        self.assertEqual(self.bundle.tests_get_last_action(), self.action_idl)


    def test_hero_killed(self):
        self.hero.health = 0
        self.bundle.process_turn(1)
        self.assertEqual(len(self.bundle.actions), 1)
        self.assertEqual(self.bundle.tests_get_last_action(), self.action_idl)
        self.assertTrue(not self.hero.is_alive)


    def test_full_battle(self):
        while len(self.bundle.actions) != 1:
            self.bundle.process_turn(1)
