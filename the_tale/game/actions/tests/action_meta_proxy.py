# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic import create_test_map
from the_tale.game.logic_storage import LogicStorage
from the_tale.game.prototypes import TimePrototype
from the_tale.game.bundles import BundlePrototype
from the_tale.game.actions.prototypes import ActionMetaProxyPrototype
from the_tale.game.actions.meta_actions import MetaActionArenaPvP1x1Prototype
from the_tale.game.actions import relations

from the_tale.game.pvp.models import BATTLE_1X1_STATE
from the_tale.game.pvp.tests.helpers import PvPTestsMixin

class MetaProxyActionForArenaPvP1x1Tests(testcase.TestCase, PvPTestsMixin):

    @mock.patch('the_tale.game.actions.prototypes.ActionBase.get_description', lambda self: 'abrakadabra')
    def setUp(self):
        super(MetaProxyActionForArenaPvP1x1Tests, self).setUp()

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

        self.action_idl_1 = self.hero_1.actions.current_action
        self.action_idl_2 = self.hero_2.actions.current_action

        self.pvp_create_battle(self.account_1, self.account_2, BATTLE_1X1_STATE.PROCESSING)
        self.pvp_create_battle(self.account_2, self.account_1, BATTLE_1X1_STATE.PROCESSING)

        bundle = BundlePrototype.create()

        meta_action_battle = MetaActionArenaPvP1x1Prototype.create(self.storage, self.hero_1, self.hero_2, bundle=bundle)

        self.action_proxy_1 = ActionMetaProxyPrototype.create(hero=self.hero_1, _bundle_id=bundle.id, meta_action=meta_action_battle)
        self.action_proxy_2 = ActionMetaProxyPrototype.create(hero=self.hero_2, _bundle_id=bundle.id, meta_action=meta_action_battle)

        self.storage.merge_bundles([self.action_idl_1.bundle_id, self.action_idl_2.bundle_id], bundle.id)

        self.meta_action_battle = self.storage.meta_actions.values()[0]


    def tearDown(self):
        pass

    def test_create(self):
        self.assertFalse(self.action_idl_1.leader)
        self.assertFalse(self.action_idl_2.leader)
        self.assertTrue(self.action_proxy_1.leader)
        self.assertTrue(self.action_proxy_2.leader)
        self.assertEqual(self.hero_1.actions.number, 2)
        self.assertEqual(self.hero_2.actions.number, 2)

        self.assertNotEqual(self.action_proxy_1.bundle_id, self.action_idl_1.bundle_id)
        self.assertNotEqual(self.action_proxy_2.bundle_id, self.action_idl_2.bundle_id)
        self.assertEqual(self.action_proxy_1.bundle_id, self.action_proxy_2.bundle_id)

        self.assertEqual(self.action_proxy_1.meta_action, self.action_proxy_2.meta_action)
        self.assertEqual(self.action_proxy_1.meta_action, self.meta_action_battle)

        self.assertEqual(len(self.storage.meta_actions), 1)

    def test_one_action_step_one_meta_step(self):
        with mock.patch('the_tale.game.actions.meta_actions.MetaActionArenaPvP1x1Prototype._process') as meta_action_process_counter:
            self.action_proxy_1.process()

        self.assertEqual(meta_action_process_counter.call_count, 1)

    def test_two_actions_step_one_meta_step(self):
        with mock.patch('the_tale.game.actions.meta_actions.MetaActionArenaPvP1x1Prototype._process') as meta_action_process_counter:
            self.action_proxy_1.process()
            self.action_proxy_2.process()

        self.assertEqual(meta_action_process_counter.call_count, 1)

    def test_two_actions_step_one_meta_step_from_storage(self):
        with mock.patch('the_tale.game.actions.meta_actions.MetaActionArenaPvP1x1Prototype._process') as meta_action_process_counter:
            self.storage.process_turn()

        self.assertEqual(meta_action_process_counter.call_count, 1)

    def test_success_processing(self):
        self.action_proxy_1.process()

        self.assertEqual(self.action_proxy_1.percents, self.meta_action_battle.percents)
        self.assertNotEqual(self.action_proxy_2.percents, self.meta_action_battle.percents)

    def test_full_battle(self):
        current_time = TimePrototype.get_current_time()

        while self.action_proxy_1.state != MetaActionArenaPvP1x1Prototype.STATE.PROCESSED:
            self.storage.process_turn(second_step_if_needed=False)
            current_time.increment_turn()

        self.assertEqual(self.meta_action_battle.state, MetaActionArenaPvP1x1Prototype.STATE.PROCESSED)
        self.assertTrue(self.hero_1.is_alive and self.hero_2.is_alive)

        self.assertTrue(self.action_idl_1.leader)
        self.assertTrue(self.action_idl_2.leader)

    def test_get_meta_action__without_storage(self):
        self.action_proxy_1.storage = None
        self.assertEqual(self.action_proxy_1.meta_action, None)

    def test_get_meta_action__no_meta_action_id(self):
        self.action_proxy_1.meta_action_id = None
        self.assertEqual(self.action_proxy_1.meta_action, None)

    def test_get_meta_action__no_meta_action(self):
        self.storage.meta_actions = {}
        self.assertEqual(self.action_proxy_1.meta_action, None)

    def test_get_meta_action(self):
        self.assertEqual(self.action_proxy_1.meta_action.id, self.meta_action_battle.id)

    def test_get_ui_type__without_storage(self):
        self.action_proxy_1.storage = None
        self.assertEqual(self.action_proxy_1.ui_type, relations.ACTION_TYPE.META_PROXY.value)

    def test_get_ui_type__with_metaaction(self):
        self.assertEqual(self.action_proxy_1.ui_type, relations.ACTION_TYPE.ARENA_PVP_1X1.value)

    def test_get_ui_type__without_metaaction(self):
        self.storage.meta_actions = {}
        self.assertEqual(self.action_proxy_1.ui_type, relations.ACTION_TYPE.META_PROXY.value)
