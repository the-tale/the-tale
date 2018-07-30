
import smart_imports

smart_imports.all()


class ArenaPvP1x1LeaveQueueAbilityTest(helpers.UseAbilityTaskMixin, utils_testcase.TestCase):
    PROCESSOR = deck.arena_pvp_1x1_leave_queue.ArenaPvP1x1LeaveQueue

    def setUp(self):
        super(ArenaPvP1x1LeaveQueueAbilityTest, self).setUp()
        self.p1, self.p2, self.p3 = game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account)

        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.ability = self.PROCESSOR()

        amqp_environment.environment.deinitialize()
        amqp_environment.environment.initialize()

        self.pvp_balancer = amqp_environment.environment.workers.pvp_balancer
        self.pvp_balancer.process_initialize('pvp_balancer')

    def test_use_no_battle(self):

        with mock.patch('the_tale.game.pvp.workers.balancer.Worker.leave_arena_queue') as balancer_cmd_counter:
            self.assertEqual(self.ability.use(**self.use_attributes(storage=self.storage, hero=self.hero)),
                             (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(balancer_cmd_counter.call_count, 0)

    def test_use_waiting_battle_state(self):

        self.pvp_balancer.add_to_arena_queue(self.hero.id)

        result, step, postsave_actions = self.ability.use(**self.use_attributes(hero=self.hero, storage=self.storage))

        self.assertEqual((result, step), (game_postponed_tasks.ComplexChangeTask.RESULT.CONTINUE, game_postponed_tasks.ComplexChangeTask.STEP.PVP_BALANCER))
        self.assertEqual(len(postsave_actions), 1)

        with mock.patch('the_tale.game.pvp.workers.balancer.Worker.cmd_logic_task') as pvp_balancer_logic_task_counter:
            postsave_actions[0]()

        self.assertEqual(pvp_balancer_logic_task_counter.call_count, 1)

        self.assertEqual(pvp_models.Battle1x1.objects.filter(state=pvp_relations.BATTLE_1X1_STATE.WAITING).count(), 1)

        result, step, postsave_actions = self.ability.use(**self.use_attributes(hero=self.hero,
                                                                                step=step,
                                                                                pvp_balancer=self.pvp_balancer))

        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(pvp_models.Battle1x1.objects.filter(state=pvp_relations.BATTLE_1X1_STATE.WAITING).count(), 0)
        self.assertEqual(pvp_models.Battle1x1.objects.all().count(), 0)

    def test_update_habits(self):
        self.pvp_balancer.add_to_arena_queue(self.hero.id)

        with mock.patch('the_tale.game.heroes.objects.Hero.update_habits') as update_habits:
            self.assertEqual(self.ability.use(**self.use_attributes(hero=self.hero, storage=self.storage))[:2],
                             (game_postponed_tasks.ComplexChangeTask.RESULT.CONTINUE, game_postponed_tasks.ComplexChangeTask.STEP.PVP_BALANCER))

        self.assertEqual(update_habits.call_args_list, [mock.call(heroes_relations.HABIT_CHANGE_SOURCE.ARENA_LEAVE)])
