# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.logic import create_test_map
from the_tale.game.actions.prototypes import ActionTradingPrototype
from the_tale.game.artifacts.storage import artifacts_storage
from the_tale.game.artifacts.relations import RARITY
from the_tale.game.prototypes import TimePrototype

class TradingActionTest(testcase.TestCase):

    def setUp(self):
        super(TradingActionTest, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]
        self.action_idl = self.hero.actions.current_action

        self.action_trade = ActionTradingPrototype.create(hero=self.hero)

    def tearDown(self):
        pass


    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_trade.leader, True)
        self.assertEqual(self.action_trade.bundle_id, self.action_idl.bundle_id)
        self.storage._test_save()

    def test_processed(self):
        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)
        self.storage._test_save()

    def test_sell_and_finish(self):

        old_money_statistics = self.hero.statistics.money_earned
        old_money = self.hero.money

        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level, rarity=RARITY.NORMAL)
        self.hero.bag.put_artifact(artifact)

        self.action_trade.percents_barier = 1

        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)

        self.assertTrue(self.hero.money > old_money)
        self.assertTrue(self.hero.statistics.money_earned > old_money_statistics)
        self.storage._test_save()

    def test_sell_and_continue(self):
        old_money = self.hero.money

        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level, rarity=RARITY.NORMAL)
        self.hero.bag.put_artifact(artifact)

        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level, rarity=RARITY.NORMAL)
        self.hero.bag.put_artifact(artifact)

        self.assertEqual(self.hero.bag.occupation, 2)

        self.action_trade.percents_barier = 2

        current_time = TimePrototype.get_current_time()

        self.storage.process_turn()
        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action, self.action_trade)
        self.assertEqual(self.hero.bag.occupation, 1)

        self.assertTrue(self.hero.money > old_money)

        old_money = self.hero.money

        current_time.increment_turn()

        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)

        self.assertEqual(self.hero.bag.occupation, 0)

        self.assertTrue(self.hero.money > old_money)
        self.storage._test_save()

    def test_stop_when_quest_required_replane(self):

        self.action_idl.percents = 0.0

        self.assertFalse(self.action_trade.replane_required)

        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level, rarity=RARITY.NORMAL)
        self.hero.bag.put_artifact(artifact)

        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level, rarity=RARITY.NORMAL)
        self.hero.bag.put_artifact(artifact)

        self.action_trade.percents_barier = 2

        self.assertEqual(self.hero.bag.occupation, 2)

        current_time = TimePrototype.get_current_time()

        self.storage.process_turn()

        self.assertEqual(self.hero.bag.occupation, 1)
        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action, self.action_trade)

        self.action_trade.replane_required = True

        current_time.increment_turn()

        self.storage.process_turn()
        self.assertEqual(self.hero.bag.occupation, 1)
        self.assertEqual(len(self.hero.actions.actions_list), 1)

        self.assertEqual(self.action_trade.state, self.action_trade.STATE.PROCESSED)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)
