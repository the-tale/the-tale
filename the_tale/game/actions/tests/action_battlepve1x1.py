# coding: utf-8
import mock

from django.test import TestCase

from game.heroes.logic import create_mob_for_hero
from game.logic import create_test_bundle, create_test_map, test_bundle_save
from game.actions.prototypes import ActionBattlePvE1x1Prototype
from game.prototypes import TimePrototype

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
        test_bundle_save(self, self.bundle)

    @mock.patch('game.actions.prototypes.battle.make_turn', lambda a, b, c: None)
    def test_mob_killed(self):
        self.assertEqual(self.hero.statistics.pve_kills, 0)
        self.action_battle.mob.health = 0
        self.bundle.process_turn()
        self.assertEqual(len(self.bundle.actions), 1)
        self.assertEqual(self.bundle.tests_get_last_action(), self.action_idl)
        self.assertEqual(self.hero.statistics.pve_kills, 1)
        test_bundle_save(self, self.bundle)


    @mock.patch('game.balance.formulas.artifacts_per_battle', lambda lvl: 0)
    @mock.patch('game.balance.constants.GET_LOOT_PROBABILITY', 1)
    @mock.patch('game.actions.prototypes.battle.make_turn', lambda a, b, c: None)
    def test_loot(self):
        self.assertEqual(self.hero.statistics.loot_had, 0)
        self.assertEqual(len(self.hero.bag.items()), 0)
        self.action_battle.mob.health = 0
        self.bundle.process_turn()
        self.assertEqual(self.hero.statistics.loot_had, 1)
        self.assertEqual(len(self.hero.bag.items()), 1)
        test_bundle_save(self, self.bundle)

    @mock.patch('game.balance.formulas.artifacts_per_battle', lambda lvl: 1)
    @mock.patch('game.actions.prototypes.battle.make_turn', lambda a, b, c: None)
    def test_artifacts(self):
        self.assertEqual(self.hero.statistics.artifacts_had, 0)
        self.assertEqual(len(self.hero.bag.items()), 0)
        self.action_battle.mob.health = 0
        self.bundle.process_turn()
        self.assertEqual(self.hero.statistics.artifacts_had, 1)
        self.assertEqual(len(self.hero.bag.items()), 1)
        test_bundle_save(self, self.bundle)

    @mock.patch('game.actions.prototypes.battle.make_turn', lambda a, b, c: None)
    def test_hero_killed(self):
        self.assertEqual(self.hero.statistics.pve_deaths, 0)
        self.hero.health = 0
        self.bundle.process_turn()
        self.assertEqual(len(self.bundle.actions), 1)
        self.assertEqual(self.bundle.tests_get_last_action(), self.action_idl)
        self.assertTrue(not self.hero.is_alive)
        self.assertEqual(self.hero.statistics.pve_deaths, 1)
        test_bundle_save(self, self.bundle)

    def test_full_battle(self):

        current_time = TimePrototype.get_current_time()

        while len(self.bundle.actions) != 1:
            self.bundle.process_turn()
            current_time.increment_turn()
        test_bundle_save(self, self.bundle)

    def test_bit_mob(self):
        old_mob_health = self.action_battle.mob.health
        old_action_percents = self.action_battle.percents

        self.action_battle.bit_mob(0.33)

        self.assertTrue(self.action_battle.mob.health < old_mob_health)
        self.assertTrue(self.action_battle.percents > old_action_percents)
        self.assertTrue(self.action_battle.updated)
