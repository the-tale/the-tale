# coding: utf-8
import mock

from dext.settings import settings

from common.utils import testcase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.heroes.prototypes import HeroPrototype

from game.actions.prototypes import ActionRegenerateEnergyPrototype, ActionMetaProxyPrototype
from game.actions.meta_actions import MetaActionArenaPvP1x1Prototype

from game.logic import create_test_map
from game.logic_storage import LogicStorage
from game.exceptions import GameException


class LogicStorageTestsBasic(testcase.TestCase):

    def setUp(self):
        settings.refresh()

        self.p1, self.p2, self.p3 = create_test_map()

        self.storage = LogicStorage()


    def test_initialize(self):
        self.assertEqual(self.storage.heroes, {})
        self.assertEqual(self.storage.actions, {})
        self.assertEqual(self.storage.heroes_to_actions, {})
        self.assertEqual(self.storage.meta_actions, {})
        self.assertEqual(self.storage.meta_actions_to_actions, {})
        self.assertEqual(self.storage.save_required, set())
        self.assertEqual(self.storage.skipped_heroes, set())
        self.assertEqual(self.storage.accounts_to_heroes, {})


class LogicStorageTests(testcase.TestCase):

    def setUp(self):
        settings.refresh()

        self.p1, self.p2, self.p3 = create_test_map()

        self.storage = LogicStorage()

        result, account_1_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')
        result, account_2_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)
        self.account_2 = AccountPrototype.get_by_id(account_2_id)

        self.storage.load_account_data(AccountPrototype.get_by_id(account_1_id))
        self.storage.load_account_data(AccountPrototype.get_by_id(account_2_id))

        self.hero_1 = self.storage.accounts_to_heroes[account_1_id]
        self.hero_2 = self.storage.accounts_to_heroes[account_2_id]

        self.action_idl_1 = self.storage.heroes_to_actions[self.hero_1.id][-1]
        self.action_idl_2 = self.storage.heroes_to_actions[self.hero_2.id][-1]

    def test_load_account_data(self):
        self.assertEqual(len(self.storage.heroes), 2)
        self.assertEqual(len(self.storage.accounts_to_heroes), 2)
        self.assertEqual(len(self.storage.actions), 2)
        self.assertEqual(len(self.storage.heroes_to_actions), 2)
        self.assertEqual(len(self.storage.save_required), 0)

        action_regenerate = ActionRegenerateEnergyPrototype.create(self.action_idl_1)

        self.assertEqual(self.action_idl_1.storage, self.storage)
        self.assertEqual(action_regenerate.storage, self.storage)

        self.assertEqual(len(self.storage.actions), 3)
        self.assertEqual(len(self.storage.heroes_to_actions), 2)
        self.assertEqual(len(self.storage.heroes_to_actions[self.hero_1.id]), 2)
        self.assertEqual(len(self.storage.heroes_to_actions[self.hero_2.id]), 1)

        storage = LogicStorage()
        storage.load_account_data(AccountPrototype.get_by_id(self.account_1.id))
        storage.load_account_data(AccountPrototype.get_by_id(self.account_2.id))
        self.assertEqual(len(storage.heroes), 2)
        self.assertEqual(len(storage.accounts_to_heroes), 2)
        self.assertEqual(len(storage.actions), 3)
        self.assertEqual(len(storage.heroes_to_actions), 2)
        self.assertEqual(len(storage.heroes_to_actions[self.hero_1.id]), 2)
        self.assertEqual(len(storage.heroes_to_actions[self.hero_2.id]), 1)

        # test order
        self.assertEqual(storage.heroes_to_actions[self.hero_1.id][0], self.action_idl_1)
        self.assertEqual(storage.heroes_to_actions[self.hero_1.id][1].TYPE, ActionRegenerateEnergyPrototype.TYPE)

    def test_load_account_data_with_meta_action(self):
        meta_action_battle = MetaActionArenaPvP1x1Prototype.create(self.storage, self.hero_1, self.hero_2)

        proxy_action_1 = ActionMetaProxyPrototype.create(self.action_idl_1, meta_action_battle)
        proxy_action_2 = ActionMetaProxyPrototype.create(self.action_idl_2, meta_action_battle)

        self.assertEqual(len(self.storage.actions), 4)
        self.assertEqual(len(self.storage.meta_actions), 1)
        self.assertEqual(len(self.storage.meta_actions_to_actions), 1)
        self.assertEqual(self.storage.meta_actions_to_actions[meta_action_battle.id], set([proxy_action_1.id, proxy_action_2.id]))

        storage = LogicStorage()
        storage.load_account_data(AccountPrototype.get_by_id(self.account_1.id))
        storage.load_account_data(AccountPrototype.get_by_id(self.account_2.id))

        self.assertEqual(len(storage.actions), 4)
        self.assertEqual(len(storage.meta_actions), 1)
        self.assertEqual(len(storage.meta_actions_to_actions), 1)
        self.assertEqual(storage.meta_actions_to_actions[meta_action_battle.id], set([proxy_action_1.id, proxy_action_2.id]))


    def test_add_duplicate_hero(self):
        self.assertRaises(GameException, self.storage.add_hero, self.hero_1)


    def test_action_release_account_data(self):

        ActionRegenerateEnergyPrototype.create(self.action_idl_1)

        self.storage.skipped_heroes.add(self.hero_1.id)

        self.storage.release_account_data(AccountPrototype.get_by_id(self.account_1.id))

        self.assertEqual(len(self.storage.heroes), 1)
        self.assertEqual(len(self.storage.accounts_to_heroes), 1)
        self.assertEqual(self.storage.heroes.values()[0].id, self.hero_2.id)
        self.assertEqual(len(self.storage.actions), 1)
        self.assertEqual(len(self.storage.heroes_to_actions), 1)
        self.assertFalse(self.storage.skipped_heroes)

    def test_save_hero_data(self):

        action_regenerate = ActionRegenerateEnergyPrototype.create(self.action_idl_1)

        self.hero_1.health = 1
        self.hero_2.health = 1

        self.action_idl_1.updated = True
        action_regenerate.updated = True

        self.storage.save_hero_data(self.hero_1.id, update_cache=False)

        self.assertEqual(self.hero_1.health, HeroPrototype.get_by_id(self.hero_1.id).health)
        self.assertNotEqual(self.hero_2.health, HeroPrototype.get_by_id(self.hero_2.id).health)

        self.assertFalse(self.action_idl_1.updated)
        self.assertFalse(action_regenerate.updated)

    def test_save_hero_data_with_meta_action(self):

        meta_action_battle = MetaActionArenaPvP1x1Prototype.create(self.storage, self.hero_1, self.hero_2)

        ActionMetaProxyPrototype.create(self.action_idl_1, meta_action_battle)
        ActionMetaProxyPrototype.create(self.action_idl_2, meta_action_battle)

        with mock.patch('game.actions.meta_actions.MetaActionPrototype.save') as save_counter:
            self.storage.save_hero_data(self.hero_1.id, update_cache=False)
            self.storage.save_hero_data(self.hero_2.id, update_cache=False)

        self.assertEqual(save_counter.call_count, 0)

        self.storage.meta_actions.values()[0].updated = True
        with mock.patch('game.actions.meta_actions.MetaActionPrototype.save', save_counter):
            self.storage.save_hero_data(self.hero_1.id, update_cache=False)
            self.storage.save_hero_data(self.hero_2.id, update_cache=False)

        self.assertEqual(save_counter.call_count, 0) # meta action saved by proxy actions

        self.storage.heroes_to_actions[self.hero_1.id][-1].updated = True
        self.storage.heroes_to_actions[self.hero_2.id][-1].updated = True

        with mock.patch('game.actions.meta_actions.MetaActionPrototype.save', save_counter):
            self.storage.save_hero_data(self.hero_1.id, update_cache=False)
            self.storage.save_hero_data(self.hero_2.id, update_cache=False)

        self.assertEqual(save_counter.call_count, 2) # meta action saved by every proxy actions


    def test_process_turn(self):
        self.assertEqual(len(self.storage.save_required), 0)

        self.storage.process_turn()

        self.assertEqual(len(self.storage.save_required), 2)


    def test_process_turn_with_skipped_hero(self):
        self.assertEqual(len(self.storage.save_required), 0)

        self.storage.skipped_heroes.add(self.hero_1.id)

        with mock.patch('game.workers.supervisor.Worker.cmd_account_release_required'):
            self.storage.process_turn()

        self.assertEqual(len(self.storage.save_required), 1)

    def test_save_changed_data(self):
        self.storage.process_turn()

        with mock.patch('dext.utils.cache.set_many') as set_many:
            with mock.patch('game.heroes.prototypes.HeroPrototype.cached_ui_info') as cached_ui_info:
                self.storage.save_changed_data()

        self.assertEqual(set_many.call_count, 1)
        self.assertEqual(cached_ui_info.call_count, 2)
        self.assertEqual(cached_ui_info.call_args, mock.call(from_cache=False))
