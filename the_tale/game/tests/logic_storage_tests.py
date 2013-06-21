# coding: utf-8
import mock

from common.utils import testcase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.heroes.prototypes import HeroPrototype

from game.actions.prototypes import ActionRegenerateEnergyPrototype, ActionMetaProxyPrototype
from game.actions.meta_actions import MetaActionArenaPvP1x1Prototype

from game.logic import create_test_map
from game.logic_storage import LogicStorage
from game.exceptions import GameException
from game.prototypes import TimePrototype
from game.bundles import BundlePrototype


class LogicStorageTestsBasic(testcase.TestCase):

    def setUp(self):
        super(LogicStorageTestsBasic, self).setUp()

        self.p1, self.p2, self.p3 = create_test_map()

        self.storage = LogicStorage()


    def test_initialize(self):
        self.assertEqual(self.storage.heroes, {})
        self.assertEqual(self.storage.meta_actions, {})
        self.assertEqual(self.storage.meta_actions_to_actions, {})
        self.assertEqual(self.storage.save_required, set())
        self.assertEqual(self.storage.skipped_heroes, set())
        self.assertEqual(self.storage.accounts_to_heroes, {})


class LogicStorageTests(testcase.TestCase):

    def setUp(self):
        super(LogicStorageTests, self).setUp()

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

        self.action_idl_1 = self.hero_1.actions.current_action
        self.action_idl_2 = self.hero_2.actions.current_action

    def test_load_account_data(self):
        self.assertEqual(len(self.storage.heroes), 2)
        self.assertEqual(len(self.storage.accounts_to_heroes), 2)
        self.assertEqual(len(self.storage.save_required), 0)

        action_regenerate = ActionRegenerateEnergyPrototype.create(hero=self.hero_1)

        self.assertEqual(self.action_idl_1.storage, self.storage)
        self.assertEqual(action_regenerate.storage, self.storage)

        storage = LogicStorage()
        storage.load_account_data(AccountPrototype.get_by_id(self.account_1.id))
        storage.load_account_data(AccountPrototype.get_by_id(self.account_2.id))
        self.assertEqual(len(storage.heroes), 2)
        self.assertEqual(len(storage.accounts_to_heroes), 2)

    def test_load_account_data_with_meta_action(self):
        bundle = BundlePrototype.create()

        meta_action_battle = MetaActionArenaPvP1x1Prototype.create(self.storage, self.hero_1, self.hero_2, bundle=bundle)

        proxy_action_1 = ActionMetaProxyPrototype.create(hero=self.hero_1, _bundle_id=bundle.id, meta_action=meta_action_battle)
        proxy_action_2 = ActionMetaProxyPrototype.create(hero=self.hero_2, _bundle_id=bundle.id, meta_action=meta_action_battle)

        self.assertEqual(len(self.storage.meta_actions), 1)
        self.assertEqual(len(self.storage.meta_actions_to_actions), 1)
        self.assertEqual(self.storage.meta_actions_to_actions[meta_action_battle.id], set([LogicStorage.get_action_uid(proxy_action_1),
                                                                                           LogicStorage.get_action_uid(proxy_action_2)]))

        self.storage.save_required.add(self.hero_1.id)
        self.storage.save_required.add(self.hero_2.id)
        self.storage.save_changed_data()

        storage = LogicStorage()
        storage.load_account_data(AccountPrototype.get_by_id(self.account_1.id))
        storage.load_account_data(AccountPrototype.get_by_id(self.account_2.id))

        self.assertEqual(len(storage.meta_actions), 1)
        self.assertEqual(len(storage.meta_actions_to_actions), 1)
        self.assertEqual(self.storage.meta_actions_to_actions[meta_action_battle.id], set([LogicStorage.get_action_uid(proxy_action_1),
                                                                                           LogicStorage.get_action_uid(proxy_action_2)]))


    def test_add_duplicate_hero(self):
        self.assertRaises(GameException, self.storage.add_hero, self.hero_1)


    def test_action_release_account_data(self):

        ActionRegenerateEnergyPrototype.create(hero=self.hero_1)

        self.storage.skipped_heroes.add(self.hero_1.id)

        self.storage.release_account_data(AccountPrototype.get_by_id(self.account_1.id))

        self.assertEqual(len(self.storage.heroes), 1)
        self.assertEqual(len(self.storage.accounts_to_heroes), 1)
        self.assertEqual(self.storage.heroes.values()[0].id, self.hero_2.id)
        self.assertFalse(self.storage.skipped_heroes)

    def test_save_hero_data(self):

        self.hero_1.health = 1
        self.hero_2.health = 1

        self.hero_1.actions.updated = True

        self.storage.save_hero_data(self.hero_1.id, update_cache=False)

        self.assertEqual(self.hero_1.health, HeroPrototype.get_by_id(self.hero_1.id).health)
        self.assertNotEqual(self.hero_2.health, HeroPrototype.get_by_id(self.hero_2.id).health)

        self.assertFalse(self.hero_1.actions.updated)

    def test_save_hero_data_with_meta_action(self):
        bundle = BundlePrototype.create()

        meta_action_battle = MetaActionArenaPvP1x1Prototype.create(self.storage, self.hero_1, self.hero_2, bundle=bundle)

        ActionMetaProxyPrototype.create(hero=self.hero_1, _bundle_id=bundle.id, meta_action=meta_action_battle)
        ActionMetaProxyPrototype.create(hero=self.hero_2, _bundle_id=bundle.id, meta_action=meta_action_battle)

        with mock.patch('game.actions.meta_actions.MetaActionPrototype.save') as save_counter:
            self.storage.save_hero_data(self.hero_1.id, update_cache=False)
            self.storage.save_hero_data(self.hero_2.id, update_cache=False)

        self.assertEqual(save_counter.call_count, 0)

        self.storage.meta_actions.values()[0].updated = True
        with mock.patch('game.actions.meta_actions.MetaActionPrototype.save', save_counter):
            self.storage.save_hero_data(self.hero_1.id, update_cache=False)
            self.storage.save_hero_data(self.hero_2.id, update_cache=False)

        self.assertEqual(save_counter.call_count, 0) # meta action saved by proxy actions

        self.hero_1.actions.updated = True
        self.hero_2.actions.updated = True

        with mock.patch('game.actions.meta_actions.MetaActionPrototype.save', save_counter):
            self.storage.save_hero_data(self.hero_1.id, update_cache=False)
            self.storage.save_hero_data(self.hero_2.id, update_cache=False)

        self.assertEqual(save_counter.call_count, 2) # meta action saved by every proxy actions (see mock.patch)


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
            with mock.patch('game.heroes.prototypes.HeroPrototype.ui_info_for_cache') as ui_info_for_cache:
                self.storage.save_changed_data()

        self.assertEqual(set_many.call_count, 1)
        self.assertEqual(ui_info_for_cache.call_count, 2)
        self.assertEqual(ui_info_for_cache.call_args, mock.call())

    def test__destroy_account_data(self):
        from game.heroes.models import Hero

        current_time = TimePrototype.get_current_time()

        # make some actions
        while self.hero_1.position.place is not None:
            self.storage.process_turn()
            current_time.increment_turn()

        self.assertEqual(Hero.objects.all().count(), 2)

        self.storage._destroy_account_data(self.account_1)
        self.storage._destroy_account_data(self.account_2)

        self.assertEqual(Hero.objects.all().count(), 0)
