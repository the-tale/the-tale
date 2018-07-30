
import smart_imports

smart_imports.all()


class ArenaPvP1x1AcceptBaseTests(helpers.UseAbilityTaskMixin, utils_testcase.TestCase):

    def setUp(self):
        super(ArenaPvP1x1AcceptBaseTests, self).setUp()

        self.p1, self.p2, self.p3 = game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1)
        self.storage.load_account_data(self.account_2)

        self.hero_1 = self.storage.accounts_to_heroes[self.account_1.id]
        self.hero_2 = self.storage.accounts_to_heroes[self.account_2.id]

        amqp_environment.environment.deinitialize()
        amqp_environment.environment.initialize()

        self.pvp_balancer = amqp_environment.environment.workers.pvp_balancer
        self.pvp_balancer.process_initialize('pvp_balancer')

        self.battle = self.pvp_balancer.add_to_arena_queue(self.hero_1.id)


class ArenaPvP1x1LeaveQueueAbilityTest(ArenaPvP1x1AcceptBaseTests):
    PROCESSOR = deck.arena_pvp_1x1_accept.ArenaPvP1x1Accept

    def setUp(self):
        super(ArenaPvP1x1LeaveQueueAbilityTest, self).setUp()
        self.ability = self.PROCESSOR()

    def use_attributes(self, step=game_postponed_tasks.ComplexChangeTask.STEP.LOGIC, storage=None, pvp_balancer=None):
        return super(ArenaPvP1x1LeaveQueueAbilityTest, self).use_attributes(hero=self.hero_2, step=step, storage=storage, pvp_balancer=pvp_balancer, battle_id=self.battle.id)

    def process_ability(self, success=True):
        result, step, postsave_actions = self.ability.use(**self.use_attributes(storage=self.storage))

        self.assertEqual((result, step), (game_postponed_tasks.ComplexChangeTask.RESULT.CONTINUE, game_postponed_tasks.ComplexChangeTask.STEP.PVP_BALANCER))
        self.assertEqual(len(postsave_actions), 1)

        with mock.patch('the_tale.game.pvp.workers.balancer.Worker.cmd_logic_task') as pvp_balancer_logic_task_counter:
            postsave_actions[0]()

        self.assertEqual(pvp_balancer_logic_task_counter.call_count, 1)

        result, step, postsave_actions = self.ability.use(**self.use_attributes(step=step, pvp_balancer=self.pvp_balancer))

        if success:
            self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))
        else:
            self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))

    def test_process_battle_not_found(self):
        pvp_models.Battle1x1.objects.all().delete()

        self.process_ability(success=False)

    def test_process_wrong_accepted_battle_state(self):
        self.battle.state = pvp_relations.BATTLE_1X1_STATE.PROCESSING
        self.battle.save()

        self.process_ability(success=False)

    def test_process_wrong_initiator_battle_state(self):
        battle = self.pvp_balancer.add_to_arena_queue(self.hero_2.id)
        battle.state = pvp_relations.BATTLE_1X1_STATE.PREPAIRING
        battle.save()

        self.process_ability(success=False)

    def test_process_battle_not_in_queue(self):
        self.pvp_balancer.arena_queue.clear()
        self.process_ability(success=False)

    # change tests order to fix sqlite segmentation fault
    def test_1_process_success(self):
        self.assertEqual(game_models.SupervisorTask.objects.all().count(), 0)

        self.process_ability()

        self.assertEqual(game_models.SupervisorTask.objects.all().count(), 1)

        self.assertEqual(pvp_prototypes.Battle1x1Prototype.get_by_id(self.battle.id).enemy_id, self.account_2.id)
        self.assertEqual(pvp_prototypes.Battle1x1Prototype.get_by_enemy_id(self.account_2.id).account_id, self.account_1.id)

    def test_process_success_when_initiator_already_has_battle_object(self):
        self.pvp_balancer.add_to_arena_queue(self.hero_2.id)

        self.assertEqual(game_models.SupervisorTask.objects.all().count(), 0)

        self.process_ability()

        self.assertEqual(game_models.SupervisorTask.objects.all().count(), 1)

        self.assertEqual(pvp_prototypes.Battle1x1Prototype.get_by_id(self.battle.id).enemy_id, self.account_2.id)
        self.assertEqual(pvp_prototypes.Battle1x1Prototype.get_by_enemy_id(self.account_2.id).account_id, self.account_1.id)

    def test_update_habits(self):
        with mock.patch('the_tale.game.heroes.objects.Hero.update_habits') as update_habits:
            self.ability.use(**self.use_attributes(storage=self.storage))

        self.assertEqual(update_habits.call_args_list, [mock.call(heroes_relations.HABIT_CHANGE_SOURCE.ARENA_SEND)])


class AcceptBattleMethodTests(ArenaPvP1x1AcceptBaseTests):

    def setUp(self):
        super(AcceptBattleMethodTests, self).setUp()

    def accept_battle(self):
        return deck.arena_pvp_1x1_accept.ArenaPvP1x1Accept.accept_battle(self.pvp_balancer, self.battle.id, self.hero_2.id)

    def test_process_battle_not_found(self):
        pvp_models.Battle1x1.objects.all().delete()

        self.assertTrue(self.accept_battle().is_BATTLE_NOT_FOUND)

        self.assertEqual(game_models.SupervisorTask.objects.all().count(), 0)

    def test_process_wrong_accepted_battle_state(self):
        self.battle.state = pvp_relations.BATTLE_1X1_STATE.PROCESSING
        self.battle.save()

        self.assertTrue(self.accept_battle().is_WRONG_ACCEPTED_BATTLE_STATE)

        self.assertEqual(game_models.SupervisorTask.objects.all().count(), 0)

    def test_process_wrong_initiator_battle_state(self):
        battle = self.pvp_balancer.add_to_arena_queue(self.hero_2.id)
        battle.state = pvp_relations.BATTLE_1X1_STATE.PREPAIRING
        battle.save()

        self.assertTrue(self.accept_battle().is_WRONG_INITIATOR_BATTLE_STATE)

        self.assertEqual(game_models.SupervisorTask.objects.all().count(), 0)

    def test_process_battle_not_in_queue(self):
        self.pvp_balancer.arena_queue.clear()

        self.assertTrue(self.accept_battle().is_NOT_IN_QUEUE)

        self.assertEqual(game_models.SupervisorTask.objects.all().count(), 0)

    # change tests order to fix sqlite segmentation fault
    def test_1_process_success(self):
        self.assertEqual(game_models.SupervisorTask.objects.all().count(), 0)

        self.assertTrue(self.accept_battle().is_PROCESSED)

        self.assertEqual(game_models.SupervisorTask.objects.all().count(), 1)

        self.assertEqual(pvp_prototypes.Battle1x1Prototype.get_by_id(self.battle.id).enemy_id, self.account_2.id)
        self.assertEqual(pvp_prototypes.Battle1x1Prototype.get_by_enemy_id(self.account_2.id).account_id, self.account_1.id)

    def test_process_success_when_initiator_already_has_battle_object(self):
        self.pvp_balancer.add_to_arena_queue(self.hero_2.id)

        self.assertEqual(game_models.SupervisorTask.objects.all().count(), 0)

        self.assertTrue(self.accept_battle().is_PROCESSED)

        self.assertEqual(game_models.SupervisorTask.objects.all().count(), 1)

        self.assertEqual(pvp_prototypes.Battle1x1Prototype.get_by_id(self.battle.id).enemy_id, self.account_2.id)
        self.assertEqual(pvp_prototypes.Battle1x1Prototype.get_by_enemy_id(self.account_2.id).account_id, self.account_1.id)
