
import smart_imports

smart_imports.all()


class ArenaPvP1x1AbilityTest(helpers.UseAbilityTaskMixin, utils_testcase.TestCase):
    PROCESSOR = deck.arena_pvp_1x1.ArenaPvP1x1

    def setUp(self):
        super(ArenaPvP1x1AbilityTest, self).setUp()

        self.p1, self.p2, self.p3 = game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account(is_fast=True)

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1)
        self.storage.load_account_data(self.account_2)

        self.hero_1 = self.storage.accounts_to_heroes[self.account_1.id]
        self.hero_2 = self.storage.accounts_to_heroes[self.account_2.id]

        self.ability_1 = self.PROCESSOR()
        self.ability_2 = self.PROCESSOR()

        amqp_environment.environment.deinitialize()
        amqp_environment.environment.initialize()

        self.pvp_balancer = amqp_environment.environment.workers.pvp_balancer
        self.pvp_balancer.process_initialize('pvp_balancer')

    def test_use(self):
        result, step, postsave_actions = self.ability_1.use(**self.use_attributes(hero=self.hero_1, storage=self.storage))

        self.assertEqual((result, step), (game_postponed_tasks.ComplexChangeTask.RESULT.CONTINUE, game_postponed_tasks.ComplexChangeTask.STEP.PVP_BALANCER))
        self.assertEqual(len(postsave_actions), 1)

        with mock.patch('the_tale.game.pvp.workers.balancer.Worker.cmd_logic_task') as pvp_balancer_logic_task_counter:
            postsave_actions[0]()

        self.assertEqual(pvp_balancer_logic_task_counter.call_count, 1)

        self.assertEqual(pvp_models.Battle1x1.objects.all().count(), 0)

        result, step, postsave_actions = self.ability_1.use(**self.use_attributes(hero=self.hero_1,
                                                                                  step=step,
                                                                                  pvp_balancer=self.pvp_balancer))

        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(pvp_models.Battle1x1.objects.all().count(), 1)

        battle = pvp_models.Battle1x1.objects.all()[0]
        self.assertEqual(battle.account.id, self.account_1.id)
        self.assertEqual(battle.enemy, None)

    def test_use__for_existed_battle(self):
        result, step, postsave_actions = self.ability_1.use(**self.use_attributes(hero=self.hero_1, storage=self.storage))

        self.assertEqual((result, step), (game_postponed_tasks.ComplexChangeTask.RESULT.CONTINUE, game_postponed_tasks.ComplexChangeTask.STEP.PVP_BALANCER))
        self.assertEqual(len(postsave_actions), 1)

        with mock.patch('the_tale.game.pvp.workers.balancer.Worker.cmd_logic_task') as pvp_balancer_logic_task_counter:
            postsave_actions[0]()

        self.assertEqual(pvp_balancer_logic_task_counter.call_count, 1)

        self.assertEqual(pvp_models.Battle1x1.objects.all().count(), 0)

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
                        (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(pvp_models.Battle1x1.objects.all().count(), 1)

        battle = pvp_models.Battle1x1.objects.all()[0]
        self.assertEqual(battle.account.id, self.account_1.id)
        self.assertEqual(battle.enemy, None)

    def test_use_for_fast_account(self):
        self.assertEqual(pvp_models.Battle1x1.objects.all().count(), 0)

        self.assertEqual(self.ability_2.use(**self.use_attributes(hero=self.hero_2, storage=self.storage)), (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))

        self.assertEqual(pvp_models.Battle1x1.objects.all().count(), 0)

    def test_update_habits(self):
        with mock.patch('the_tale.game.heroes.objects.Hero.update_habits') as update_habits:
            self.ability_1.use(**self.use_attributes(hero=self.hero_1, storage=self.storage))

        self.assertEqual(update_habits.call_args_list, [mock.call(heroes_relations.HABIT_CHANGE_SOURCE.ARENA_SEND)])
