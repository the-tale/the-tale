# coding: utf-8
import mock

from dext.settings import settings

from common.utils.testcase import TestCase, CallCounter

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.logic import create_test_map
from game.logic_storage import LogicStorage
from game.prototypes import TimePrototype
from game.actions.prototypes import ActionMetaProxyPrototype
from game.actions.meta_actions import MetaActionArenaPvP1x1Prototype

from game.pvp.models import BATTLE_1X1_STATE
from game.pvp.tests.helpers import PvPTestsMixin

class MetaProxyActionForArenaPvP1x1Tests(TestCase, PvPTestsMixin):

    @mock.patch('game.actions.prototypes.ActionPrototype.get_description', lambda self: 'abrakadabra')
    def setUp(self):
        settings.refresh()

        create_test_map()

        result, account_1_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')
        result, account_2_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)
        self.account_2 = AccountPrototype.get_by_id(account_2_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(self.account_1.id))
        self.storage.load_account_data(AccountPrototype.get_by_id(self.account_2.id))

        self.hero_1 = self.storage.accounts_to_heroes[account_1_id]
        self.hero_2 = self.storage.accounts_to_heroes[account_2_id]

        self.action_idl_1 = self.storage.heroes_to_actions[self.hero_1.id][-1]
        self.action_idl_2 = self.storage.heroes_to_actions[self.hero_2.id][-1]

        self.pvp_create_battle(self.account_1, self.account_2, BATTLE_1X1_STATE.PROCESSING)
        self.pvp_create_battle(self.account_2, self.account_1, BATTLE_1X1_STATE.PROCESSING)

        meta_action_battle = MetaActionArenaPvP1x1Prototype.create(self.hero_1, self.hero_2)

        self.action_proxy_1 = ActionMetaProxyPrototype.create(self.action_idl_1, meta_action_battle)
        self.action_proxy_2 = ActionMetaProxyPrototype.create(self.action_idl_2, meta_action_battle)

        self.meta_action_battle = self.storage.meta_actions.values()[0]


    def tearDown(self):
        pass

    def test_create(self):
        self.assertFalse(self.action_idl_1.leader)
        self.assertFalse(self.action_idl_2.leader)
        self.assertTrue(self.action_proxy_1.leader)
        self.assertTrue(self.action_proxy_2.leader)
        self.assertEqual(len(self.hero_1.actions_descriptions), 2)
        self.assertEqual(len(self.hero_2.actions_descriptions), 2)

        # here we not test creating of new bundle (it processed and tested in supervisor tasks)
        self.assertEqual(self.action_proxy_1.bundle_id, self.action_idl_1.bundle_id)
        self.assertEqual(self.action_proxy_2.bundle_id, self.action_idl_2.bundle_id)

        self.assertEqual(self.action_proxy_1.meta_action, self.action_proxy_2.meta_action)
        self.assertEqual(self.action_proxy_1.meta_action, self.meta_action_battle)

        self.assertEqual(len(self.storage.meta_actions), 1)

    def test_one_action_step_one_meta_step(self):
        meta_action_process_counter = CallCounter()

        with mock.patch('game.actions.meta_actions.MetaActionArenaPvP1x1Prototype._process', meta_action_process_counter):
            self.action_proxy_1.process()

        self.assertEqual(meta_action_process_counter.count, 1)

    def test_two_actions_step_one_meta_step(self):
        meta_action_process_counter = CallCounter()

        with mock.patch('game.actions.meta_actions.MetaActionArenaPvP1x1Prototype._process', meta_action_process_counter):
            self.action_proxy_1.process()
            self.action_proxy_2.process()

        self.assertEqual(meta_action_process_counter.count, 1)

    def test_two_actions_step_one_meta_step_from_storage(self):
        meta_action_process_counter = CallCounter()

        with mock.patch('game.actions.meta_actions.MetaActionArenaPvP1x1Prototype._process', meta_action_process_counter):
            self.storage.process_turn()

        self.assertEqual(meta_action_process_counter.count, 1)

    def test_success_processing(self):
        self.action_proxy_1.process()

        self.assertEqual(self.action_proxy_1.percents, self.meta_action_battle.percents)
        self.assertNotEqual(self.action_proxy_2.percents, self.meta_action_battle.percents)

    def test_full_battle(self):
        current_time = TimePrototype.get_current_time()

        while self.action_proxy_1.state != MetaActionArenaPvP1x1Prototype.STATE.PROCESSED:
            self.storage.process_turn()
            current_time.increment_turn()

        self.assertEqual(self.meta_action_battle.state, MetaActionArenaPvP1x1Prototype.STATE.PROCESSED)
        self.assertTrue(self.hero_1.is_alive and self.hero_2.is_alive)

        self.assertTrue(self.action_idl_1.leader)
        self.assertTrue(self.action_idl_2.leader)
