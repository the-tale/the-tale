# coding: utf-8

import mock

from dext.settings import settings

from common.utils.testcase import TestCase, CallCounter

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.logic_storage import LogicStorage

from game.logic import create_test_map
from game.prototypes import TimePrototype

from game.actions.meta_actions import MetaActionArenaPvP1x1Prototype
from game.actions.models import MetaAction, MetaActionMember

from game.pvp.models import Battle1x1

from game.pvp.models import BATTLE_1X1_STATE
from game.pvp.tests.helpers import PvPTestsMixin

class ArenaPvP1x1MetaActionTest(TestCase, PvPTestsMixin):

    def setUp(self):
        settings.refresh()

        create_test_map()

        result, account_1_id, bundle_id = register_user('test_user_1')
        result, account_2_id, bundle_id = register_user('test_user_2')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)
        self.account_2 = AccountPrototype.get_by_id(account_2_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)
        self.storage.load_account_data(self.account_2)

        self.hero_1 = self.storage.accounts_to_heroes[self.account_1.id]
        self.hero_2 = self.storage.accounts_to_heroes[self.account_2.id]

        self.hero_1.health = self.hero_1.max_health / 2

        self.pvp_create_battle(self.account_1, self.account_2, BATTLE_1X1_STATE.PROCESSING)
        self.pvp_create_battle(self.account_2, self.account_1, BATTLE_1X1_STATE.PROCESSING)

        self.meta_action_battle = MetaActionArenaPvP1x1Prototype.create(self.storage, self.hero_1, self.hero_2)
        self.meta_action_battle.set_storage(self.storage)


    def test_initialization(self):
        self.assertEqual(MetaAction.objects.all().count(), 1)
        self.assertEqual(MetaActionMember.objects.all().count(), 2)

        self.assertEqual(len(self.meta_action_battle.members), 2)
        self.assertEqual(len(self.meta_action_battle.members_by_roles), 2)
        self.assertTrue(self.meta_action_battle.storage)

        self.assertEqual(self.meta_action_battle.hero_1, self.hero_1)
        self.assertEqual(self.meta_action_battle.hero_2, self.hero_2)

    def test_one_hero_killed(self):
        current_time = TimePrototype.get_current_time()
        self.hero_1.health = 0
        self.meta_action_battle.process()
        self.assertEqual(self.meta_action_battle.state, MetaActionArenaPvP1x1Prototype.STATE.BATTLE_ENDING)
        current_time.increment_turn()
        self.meta_action_battle.process()

        self.assertEqual(self.meta_action_battle.state, MetaActionArenaPvP1x1Prototype.STATE.PROCESSED)
        self.assertTrue(self.hero_1.is_alive and self.hero_2.is_alive)
        self.assertEqual(self.hero_1.health, self.hero_1.max_health / 2)
        self.assertEqual(self.hero_2.health, self.hero_2.max_health)

    def test_second_process_call_in_one_turn(self):

        meta_action_process_counter = CallCounter()

        with mock.patch('game.actions.meta_actions.MetaActionArenaPvP1x1Prototype._process', meta_action_process_counter):
            self.meta_action_battle.process()
            self.meta_action_battle.process()

        self.assertEqual(meta_action_process_counter.count, 1)

    def test_full_battle(self):
        current_time = TimePrototype.get_current_time()

        self.assertEqual(Battle1x1.objects.filter(state=BATTLE_1X1_STATE.PROCESSING).count(), 2)

        while self.meta_action_battle.state != MetaActionArenaPvP1x1Prototype.STATE.PROCESSED:
            self.meta_action_battle.process()
            current_time.increment_turn()

        self.assertEqual(self.meta_action_battle.state, MetaActionArenaPvP1x1Prototype.STATE.PROCESSED)
        self.assertTrue(self.hero_1.is_alive and self.hero_2.is_alive)
        self.assertEqual(self.hero_1.health, self.hero_1.max_health / 2)
        self.assertEqual(self.hero_2.health, self.hero_2.max_health)

        self.assertEqual(Battle1x1.objects.filter(state=BATTLE_1X1_STATE.PROCESSED).count(), 2)

    def test_remove(self):
        self.assertEqual(MetaAction.objects.all().count(), 1)
        self.assertEqual(MetaActionMember.objects.all().count(), 2)
        self.meta_action_battle.remove()
        self.assertEqual(MetaAction.objects.all().count(), 0)
        self.assertEqual(MetaActionMember.objects.all().count(), 0)
