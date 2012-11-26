# coding: utf-8
import mock

from common.utils.testcase import TestCase, CallCounter

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.logic_storage import LogicStorage
from game.logic import create_test_map

from game.abilities.deck.arena_pvp_1x1_leave_queue import ArenaPvP1x1LeaveQueue

from game.pvp.prototypes import Battle1x1Prototype


class ArenaPvP1x1LeaveQueueAbilityTest(TestCase):

    def setUp(self):
        self.p1, self.p2, self.p3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account = AccountPrototype.get_by_id(account_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)

        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.ability = ArenaPvP1x1LeaveQueue.get_by_hero_id(self.hero.id)


    def test_use_no_battle(self):

        balancer_cmd_counter = CallCounter()

        with mock.patch('game.pvp.workers.balancer.Worker.cmd_leave_arena_queue', balancer_cmd_counter):
            self.assertTrue(self.ability.use(self.storage, self.hero, None))

        self.assertEqual(balancer_cmd_counter.count, 0)

    def test_use_waiting_battle_state(self):

        Battle1x1Prototype.create(self.account)

        balancer_cmd_counter = CallCounter()

        with mock.patch('game.pvp.workers.balancer.Worker.cmd_leave_arena_queue', balancer_cmd_counter):
            self.assertTrue(self.ability.use(self.storage, self.hero, None))

        self.assertEqual(balancer_cmd_counter.count, 1)
