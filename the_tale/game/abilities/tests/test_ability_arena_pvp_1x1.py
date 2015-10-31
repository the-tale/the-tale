# coding: utf-8
import mock

from the_tale.amqp_environment import environment

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user
from the_tale.game.logic_storage import LogicStorage

from the_tale.game.logic import create_test_map
from the_tale.game.abilities.deck.arena_pvp_1x1 import ArenaPvP1x1
from the_tale.game.pvp.models import Battle1x1

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.abilities.tests.helpers import UseAbilityTaskMixin


class ArenaPvP1x1AbilityTest(UseAbilityTaskMixin, testcase.TestCase):
    PROCESSOR = ArenaPvP1x1

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

        self.ability_1 = self.PROCESSOR()
        self.ability_2 = self.PROCESSOR()

        environment.deinitialize()
        environment.initialize()

        self.pvp_balancer = environment.workers.pvp_balancer
        self.pvp_balancer.process_initialize('pvp_balancer')

    def test_use(self):

        result, step, postsave_actions = self.ability_1.use(**self.use_attributes(hero=self.hero_1, storage=self.storage))

        self.assertEqual((result, step), (ComplexChangeTask.RESULT.CONTINUE, ComplexChangeTask.STEP.PVP_BALANCER))
        self.assertEqual(len(postsave_actions), 1)

        with mock.patch('the_tale.game.pvp.workers.balancer.Worker.cmd_logic_task') as pvp_balancer_logic_task_counter:
            postsave_actions[0]()

        self.assertEqual(pvp_balancer_logic_task_counter.call_count, 1)

        self.assertEqual(Battle1x1.objects.all().count(), 0)

        result, step, postsave_actions = self.ability_1.use(**self.use_attributes(hero=self.hero_1,
                                                                                  step=step,
                                                                                  pvp_balancer=self.pvp_balancer))

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(Battle1x1.objects.all().count(), 1)

        battle = Battle1x1.objects.all()[0]
        self.assertEqual(battle.account.id, self.account_1.id)
        self.assertEqual(battle.enemy, None)

    def test_use__for_existed_battle(self):

        result, step, postsave_actions = self.ability_1.use(**self.use_attributes(hero=self.hero_1, storage=self.storage))

        self.assertEqual((result, step), (ComplexChangeTask.RESULT.CONTINUE, ComplexChangeTask.STEP.PVP_BALANCER))
        self.assertEqual(len(postsave_actions), 1)

        with mock.patch('the_tale.game.pvp.workers.balancer.Worker.cmd_logic_task') as pvp_balancer_logic_task_counter:
            postsave_actions[0]()

        self.assertEqual(pvp_balancer_logic_task_counter.call_count, 1)

        self.assertEqual(Battle1x1.objects.all().count(), 0)

        result_1, step_1, postsave_actions_1 = self.ability_1.use(**self.use_attributes(hero=self.hero_1,
                                                                                        step=step,
                                                                                        pvp_balancer=self.pvp_balancer))

        with mock.patch('the_tale.game.pvp.workers.balancer.Worker.add_to_arena_queue') as add_to_arena_queue:
            result_2, step_2, postsave_actions_2 = self.ability_1.use(**self.use_attributes(hero=self.hero_1,
                                                                                            step=step,
                                                                                            pvp_balancer=self.pvp_balancer))

        self.assertEqual(add_to_arena_queue.call_count, 0)

        self.assertTrue((result_1, step_1, postsave_actions_1) ==
                        (result_2, step_2, postsave_actions_2) ==
                        (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(Battle1x1.objects.all().count(), 1)

        battle = Battle1x1.objects.all()[0]
        self.assertEqual(battle.account.id, self.account_1.id)
        self.assertEqual(battle.enemy, None)


    def test_use_for_fast_account(self):
        self.assertEqual(Battle1x1.objects.all().count(), 0)

        self.assertEqual(self.ability_2.use(**self.use_attributes(hero=self.hero_2, storage=self.storage)), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))

        self.assertEqual(Battle1x1.objects.all().count(), 0)


    def test_update_habits(self):
        from the_tale.game.heroes.relations import HABIT_CHANGE_SOURCE

        with mock.patch('the_tale.game.heroes.objects.Hero.update_habits') as update_habits:
            self.ability_1.use(**self.use_attributes(hero=self.hero_1, storage=self.storage))

        self.assertEqual(update_habits.call_args_list, [mock.call(HABIT_CHANGE_SOURCE.ARENA_SEND)])
