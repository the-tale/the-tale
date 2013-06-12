# coding: utf-8
import mock

from common.utils import testcase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user
from game.logic_storage import LogicStorage

from game.workers.environment import workers_environment

from game.logic import create_test_map
from game.abilities.deck.arena_pvp_1x1 import ArenaPvP1x1, ABILITY_TASK_STEP
from game.pvp.models import Battle1x1

class ArenaPvP1x1AbilityTest(testcase.TestCase):

    def setUp(self):
        super(ArenaPvP1x1AbilityTest, self).setUp()
        self.p1, self.p2, self.p3 = create_test_map()


        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        result, account_2_id, bundle_id = register_user('test_user_2')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)
        self.account_2 = AccountPrototype.get_by_id(account_2_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)
        self.storage.load_account_data(self.account_2)

        self.hero_1 = self.storage.accounts_to_heroes[self.account_1.id]
        self.hero_2 = self.storage.accounts_to_heroes[self.account_2.id]

        self.ability_1 = ArenaPvP1x1()
        self.ability_2 = ArenaPvP1x1()

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


    def test_use(self):

        result, step, postsave_actions = self.ability_1.use(**self.use_attributes(hero_id=self.hero_1.id, storage=self.storage))

        self.assertEqual((result, step), (None, ABILITY_TASK_STEP.PVP_BALANCER))
        self.assertEqual(len(postsave_actions), 1)

        with mock.patch('game.pvp.workers.balancer.Worker.cmd_logic_task') as pvp_balancer_logic_task_counter:
            postsave_actions[0]()

        self.assertEqual(pvp_balancer_logic_task_counter.call_count, 1)

        self.assertEqual(Battle1x1.objects.all().count(), 0)

        result, step, postsave_actions = self.ability_1.use(**self.use_attributes(hero_id=self.hero_1.id,
                                                                                  step=step,
                                                                                  pvp_balancer=self.pvp_balancer))

        self.assertEqual((result, step, postsave_actions), (True, ABILITY_TASK_STEP.SUCCESS, ()))

        self.assertEqual(Battle1x1.objects.all().count(), 1)

        battle = Battle1x1.objects.all()[0]
        self.assertEqual(battle.account.id, self.account_1.id)
        self.assertEqual(battle.enemy, None)


    def test_use_for_fast_account(self):
        self.assertEqual(Battle1x1.objects.all().count(), 0)

        self.assertEqual(self.ability_2.use(**self.use_attributes(hero_id=self.hero_2.id, storage=self.storage)), (False, ABILITY_TASK_STEP.ERROR, ()))

        self.assertEqual(Battle1x1.objects.all().count(), 0)
