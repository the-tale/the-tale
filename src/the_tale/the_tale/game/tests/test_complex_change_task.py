
import smart_imports

smart_imports.all()


class ComplexChangeTasksTests(utils_testcase.TestCase):

    def setUp(self):
        super(ComplexChangeTasksTests, self).setUp()

        logic.create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = logic_storage.LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.task = abilities_postponed_tasks.UseAbilityTask(processor_id=abilities_relations.ABILITY_TYPE.HELP.value,
                                                             hero_id=self.hero.id,
                                                             data={'hero_id': self.hero.id,
                                                                   'transaction_id': None})

    def test_create(self):
        self.assertTrue(issubclass(abilities_postponed_tasks.UseAbilityTask, postponed_tasks.ComplexChangeTask))
        self.assertEqual(self.task.state, postponed_tasks.ComplexChangeTask.STATE.UNPROCESSED)

    def test_serialization(self):
        self.assertEqual(self.task.serialize(), abilities_postponed_tasks.UseAbilityTask.deserialize(self.task.serialize()).serialize())

    def test_response_data(self):
        self.assertEqual(self.task.processed_data, {'message': None})

    def test_banned(self):
        self.hero.ban_state_end_at = datetime.datetime.now() + datetime.timedelta(days=1)
        heroes_logic.save_hero(self.hero)
        self.assertEqual(self.task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(self.task.state, postponed_tasks.ComplexChangeTask.STATE.BANNED)

    @mock.patch('the_tale.game.abilities.prototypes.AbilityPrototype.check_hero_conditions', lambda *argv, **kwargs: False)
    def test_check_hero_conditions__failed(self):
        self.assertEqual(self.task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(self.task.state, postponed_tasks.ComplexChangeTask.STATE.HERO_CONDITIONS_NOT_PASSED)

    def test_process_can_not_process(self):

        with mock.patch('the_tale.game.abilities.deck.help.Help.use', lambda self, task, storage, pvp_balancer, highlevel: (postponed_tasks.ComplexChangeTask.RESULT.FAILED, None, ())):
            self.assertEqual(self.task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
            self.assertEqual(self.task.state, postponed_tasks.ComplexChangeTask.STATE.CAN_NOT_PROCESS)

    def test_process_success(self):
        self.assertEqual(self.task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(self.task.state, postponed_tasks.ComplexChangeTask.STATE.PROCESSED)

    def test_process_second_step_success(self):

        with mock.patch('the_tale.game.abilities.deck.help.Help.use', lambda self, task, storage, pvp_balancer, highlevel: (postponed_tasks.ComplexChangeTask.RESULT.CONTINUE, postponed_tasks.ComplexChangeTask.STEP.HIGHLEVEL, ())):
            self.assertEqual(self.task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        self.assertTrue(self.task.step.is_HIGHLEVEL)
        self.assertEqual(self.task.state, postponed_tasks.ComplexChangeTask.STATE.UNPROCESSED)

        self.assertEqual(self.task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(self.task.state, postponed_tasks.ComplexChangeTask.STATE.PROCESSED)

    def test_process_second_step_error(self):

        with mock.patch('the_tale.game.abilities.deck.help.Help.use', lambda self, task, storage, pvp_balancer, highlevel: (postponed_tasks.ComplexChangeTask.RESULT.CONTINUE, postponed_tasks.ComplexChangeTask.STEP.HIGHLEVEL, ())):
            self.assertEqual(self.task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        self.assertTrue(self.task.step.is_HIGHLEVEL)
        self.assertEqual(self.task.state, postponed_tasks.ComplexChangeTask.STATE.UNPROCESSED)

        with mock.patch('the_tale.game.abilities.deck.help.Help.use', lambda self, task, storage, pvp_balancer, highlevel: (postponed_tasks.ComplexChangeTask.RESULT.FAILED, None, ())):
            self.assertEqual(self.task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)

        self.assertEqual(self.task.state, postponed_tasks.ComplexChangeTask.STATE.CAN_NOT_PROCESS)
