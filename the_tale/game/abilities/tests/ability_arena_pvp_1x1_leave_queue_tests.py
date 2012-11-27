# coding: utf-8
import mock

from common.utils.testcase import TestCase, CallCounter

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.workers.environment import workers_environment

from game.logic_storage import LogicStorage
from game.logic import create_test_map

from game.abilities.deck.arena_pvp_1x1_leave_queue import ArenaPvP1x1LeaveQueue, ABILITY_TASK_STEP

from game.pvp.prototypes import Battle1x1Prototype
from game.pvp.models import BATTLE_1X1_STATE, Battle1x1


class ArenaPvP1x1LeaveQueueAbilityTest(TestCase):

    def setUp(self):
        self.p1, self.p2, self.p3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account = AccountPrototype.get_by_id(account_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)

        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.ability = ArenaPvP1x1LeaveQueue.get_by_hero_id(self.hero.id)

        workers_environment.deinitialize()
        workers_environment.initialize()

        self.pvp_balancer = workers_environment.pvp_balancer
        self.pvp_balancer.process_initialize('pvp_balancer')

    def use_attributes(self, hero_id, step=None, storage=None, pvp_balancer=None):
        return {'data': {'hero_id': hero_id},
                'step': step,
                'main_task_id': 0,
                'storage': storage,
                'pvp_balancer': pvp_balancer}

    def test_use_no_battle(self):

        balancer_cmd_counter = CallCounter()

        with mock.patch('game.pvp.workers.balancer.Worker.leave_arena_queue', balancer_cmd_counter):
            self.assertEqual(self.ability.use(**self.use_attributes(storage=self.storage, hero_id=self.hero.id)), (True, None, ()))

        self.assertEqual(balancer_cmd_counter.count, 0)

    def test_use_waiting_battle_state(self):

        self.pvp_balancer.add_to_arena_queue(self.hero.id)

        result, step, postsave_actions = self.ability.use(**self.use_attributes(hero_id=self.hero.id, storage=self.storage))

        self.assertEqual((result, step), (None, ABILITY_TASK_STEP.PVP_BALANCER))
        self.assertEqual(len(postsave_actions), 1)

        pvp_balancer_logic_task_counter = CallCounter()

        with mock.patch('game.pvp.workers.balancer.Worker.cmd_logic_task', pvp_balancer_logic_task_counter):
            postsave_actions[0]()

        self.assertEqual(pvp_balancer_logic_task_counter.count, 1)

        self.assertEqual(Battle1x1.objects.filter(state=BATTLE_1X1_STATE.WAITING).count(), 1)
        self.assertEqual(Battle1x1.objects.filter(state=BATTLE_1X1_STATE.LEAVE_QUEUE).count(), 0)

        result, step, postsave_actions = self.ability.use(**self.use_attributes(hero_id=self.hero.id,
                                                                                step=step,
                                                                                pvp_balancer=self.pvp_balancer))

        self.assertEqual((result, step, postsave_actions), (True, ABILITY_TASK_STEP.SUCCESS, ()))

        self.assertEqual(Battle1x1.objects.filter(state=BATTLE_1X1_STATE.WAITING).count(), 0)
        self.assertEqual(Battle1x1.objects.filter(state=BATTLE_1X1_STATE.LEAVE_QUEUE).count(), 1)
