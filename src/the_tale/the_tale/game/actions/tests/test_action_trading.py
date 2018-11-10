
import smart_imports

smart_imports.all()


class TradingActionTest(utils_testcase.TestCase):

    def setUp(self):
        super(TradingActionTest, self).setUp()

        game_logic.create_test_map()

        account = self.accounts_factory.create_account(is_fast=True)

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(account)
        self.hero = self.storage.accounts_to_heroes[account.id]
        self.action_idl = self.hero.actions.current_action

        self.action_trade = prototypes.ActionTradingPrototype.create(hero=self.hero)

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

        artifact = artifacts_storage.artifacts.generate_artifact_from_list(artifacts_storage.artifacts.artifacts,
                                                                           self.hero.level,
                                                                           rarity=artifacts_relations.RARITY.NORMAL)
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

        artifact = artifacts_storage.artifacts.generate_artifact_from_list(artifacts_storage.artifacts.artifacts,
                                                                           self.hero.level,
                                                                           rarity=artifacts_relations.RARITY.NORMAL)
        self.hero.bag.put_artifact(artifact)

        artifact = artifacts_storage.artifacts.generate_artifact_from_list(artifacts_storage.artifacts.artifacts,
                                                                           self.hero.level,
                                                                           rarity=artifacts_relations.RARITY.NORMAL)
        self.hero.bag.put_artifact(artifact)

        self.assertEqual(self.hero.bag.occupation, 2)

        self.action_trade.percents_barier = 2

        self.storage.process_turn()
        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action, self.action_trade)
        self.assertEqual(self.hero.bag.occupation, 1)

        self.assertTrue(self.hero.money > old_money)

        old_money = self.hero.money

        game_turn.increment()

        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)

        self.assertEqual(self.hero.bag.occupation, 0)

        self.assertTrue(self.hero.money > old_money)
        self.storage._test_save()

    def test_stop_when_quest_required_replane(self):

        self.action_idl.percents = 0.0

        self.assertFalse(self.action_trade.replane_required)

        artifact = artifacts_storage.artifacts.generate_artifact_from_list(artifacts_storage.artifacts.artifacts,
                                                                           self.hero.level,
                                                                           rarity=artifacts_relations.RARITY.NORMAL)
        self.hero.bag.put_artifact(artifact)

        artifact = artifacts_storage.artifacts.generate_artifact_from_list(artifacts_storage.artifacts.artifacts,
                                                                           self.hero.level,
                                                                           rarity=artifacts_relations.RARITY.NORMAL)
        self.hero.bag.put_artifact(artifact)

        self.action_trade.percents_barier = 2

        self.assertEqual(self.hero.bag.occupation, 2)

        self.storage.process_turn()

        self.assertEqual(self.hero.bag.occupation, 1)
        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action, self.action_trade)

        self.action_trade.replane_required = True

        game_turn.increment()

        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(self.hero.bag.occupation, 1)
        self.assertEqual(len(self.hero.actions.actions_list), 1)

        self.assertEqual(self.action_trade.state, self.action_trade.STATE.PROCESSED)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)
