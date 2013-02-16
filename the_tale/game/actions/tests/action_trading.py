# coding: utf-8

from django.test import TestCase

from dext.settings import settings

from accounts.logic import register_user
from game.heroes.prototypes import HeroPrototype
from game.logic_storage import LogicStorage

from game.logic import create_test_map
from game.actions.prototypes import ActionTradingPrototype
from game.artifacts.storage import artifacts_storage
from game.prototypes import TimePrototype

class TradingActionTest(TestCase):

    def setUp(self):
        settings.refresh()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)
        self.action_idl = self.storage.heroes_to_actions[self.hero.id][-1]

        self.action_trade = ActionTradingPrototype.create(self.action_idl)

    def tearDown(self):
        pass


    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_trade.leader, True)
        self.assertEqual(self.action_trade.bundle_id, self.action_idl.bundle_id)
        self.storage._test_save()

    def test_processed(self):
        self.storage.process_turn()
        self.assertEqual(len(self.storage.actions), 1)
        self.assertEqual(self.storage.heroes_to_actions[self.hero.id][-1], self.action_idl)
        self.storage._test_save()

    def test_sell_and_finish(self):

        old_money_statistics = self.hero.statistics.money_earned
        old_money = self.hero.money

        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level)
        self.hero.bag.put_artifact(artifact)

        self.action_trade.percents_barier = 1

        self.storage.process_turn()
        self.assertEqual(len(self.storage.actions), 1)
        self.assertEqual(self.storage.heroes_to_actions[self.hero.id][-1], self.action_idl)

        self.assertTrue(self.hero.money > old_money)
        self.assertTrue(self.hero.statistics.money_earned > old_money_statistics)
        self.storage._test_save()

    def test_sell_and_continue(self):
        old_money = self.hero.money

        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level)
        self.hero.bag.put_artifact(artifact)

        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level)
        self.hero.bag.put_artifact(artifact)

        self.action_trade.percents_barier = 2

        current_time = TimePrototype.get_current_time()

        self.storage.process_turn()
        self.assertEqual(len(self.storage.actions), 2)
        self.assertEqual(self.storage.heroes_to_actions[self.hero.id][-1], self.action_trade)

        self.assertTrue(self.hero.money > old_money)

        old_money = self.hero.money

        current_time.increment_turn()

        self.storage.process_turn()
        self.assertEqual(len(self.storage.actions), 1)
        self.assertEqual(self.storage.heroes_to_actions[self.hero.id][-1], self.action_idl)

        self.assertTrue(self.hero.money > old_money)
        self.storage._test_save()
