# coding: utf-8

from django.test import TestCase

from game.logic import create_test_bundle, create_test_map, test_bundle_save
from game.actions.prototypes import ActionTradingPrototype
from game.artifacts.storage import ArtifactsDatabase
from game.prototypes import TimePrototype

class TradingActionTest(TestCase):

    def setUp(self):
        create_test_map()

        self.bundle = create_test_bundle('TradingActionTest')
        self.action_idl = self.bundle.tests_get_last_action()
        self.action_trade = ActionTradingPrototype.create(self.action_idl)
        self.hero = self.bundle.tests_get_hero()


    def tearDown(self):
        pass


    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_trade.leader, True)
        test_bundle_save(self, self.bundle)

    def test_processed(self):
        self.bundle.process_turn()
        self.assertEqual(len(self.bundle.actions), 1)
        self.assertEqual(self.bundle.tests_get_last_action(), self.action_idl)
        test_bundle_save(self, self.bundle)

    def test_sell_and_finish(self):

        old_money_statistics = self.hero.statistics.money_earned
        old_money = self.hero.money

        artifact = ArtifactsDatabase.storage().generate_artifact_from_list(ArtifactsDatabase.storage().artifacts_ids, self.hero.level)
        self.hero.bag.put_artifact(artifact)

        self.action_trade.percents_barier = 1

        self.bundle.process_turn()
        self.assertEqual(len(self.bundle.actions), 1)
        self.assertEqual(self.bundle.tests_get_last_action(), self.action_idl)

        self.assertTrue(self.hero.money > old_money)
        self.assertTrue(self.hero.statistics.money_earned > old_money_statistics)
        test_bundle_save(self, self.bundle)

    def test_sell_and_continue(self):
        old_money = self.hero.money

        artifact = ArtifactsDatabase.storage().generate_artifact_from_list(ArtifactsDatabase.storage().artifacts_ids, self.hero.level)
        self.hero.bag.put_artifact(artifact)

        artifact = ArtifactsDatabase.storage().generate_artifact_from_list(ArtifactsDatabase.storage().artifacts_ids, self.hero.level)
        self.hero.bag.put_artifact(artifact)

        self.action_trade.percents_barier = 2

        current_time = TimePrototype.get_current_time()

        self.bundle.process_turn()
        self.assertEqual(len(self.bundle.actions), 2)
        self.assertEqual(self.bundle.tests_get_last_action(), self.action_trade)

        self.assertTrue(self.hero.money > old_money)

        old_money = self.hero.money

        current_time.increment_turn()

        self.bundle.process_turn()
        self.assertEqual(len(self.bundle.actions), 1)
        self.assertEqual(self.bundle.tests_get_last_action(), self.action_idl)

        self.assertTrue(self.hero.money > old_money)
        test_bundle_save(self, self.bundle)
