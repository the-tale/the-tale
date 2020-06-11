
import smart_imports

smart_imports.all()


class UseAbilityTasksTests(utils_testcase.TestCase):

    def setUp(self):
        super(UseAbilityTasksTests, self).setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account.id)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.task = postponed_tasks.UseAbilityTask(processor_id=relations.ABILITY_TYPE.HELP.value,
                                                   hero_id=self.hero.id,
                                                   data={'hero_id': self.hero.id,
                                                         'transaction_id': None})

    def test_create(self):
        self.assertEqual(self.task.state, game_postponed_tasks.ComplexChangeTask.STATE.UNPROCESSED)

    def test_serialization(self):
        self.assertEqual(self.task.serialize(), postponed_tasks.UseAbilityTask.deserialize(self.task.serialize()).serialize())

    def test_response_data(self):
        self.assertEqual(self.task.processed_data, {'message': None})

    def test_banned(self):
        self.hero.ban_state_end_at = datetime.datetime.now() + datetime.timedelta(days=1)
        heroes_logic.save_hero(self.hero)
        self.assertEqual(self.task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(self.task.state, game_postponed_tasks.ComplexChangeTask.STATE.BANNED)

    def test_process_can_not_process(self):

        with mock.patch('the_tale.game.abilities.deck.help.Help.use', lambda self, task, storage: (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, None, ())):
            self.assertEqual(self.task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
            self.assertEqual(self.task.state, game_postponed_tasks.ComplexChangeTask.STATE.CAN_NOT_PROCESS)

    def test_process_success(self):
        self.assertEqual(self.task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(self.task.state, game_postponed_tasks.ComplexChangeTask.STATE.PROCESSED)

    def test_process_success__has_transaction(self):
        energy = game_tt_services.energy.cmd_balance(self.account.id)

        status, transaction_id = game_tt_services.energy.cmd_change_balance(account_id=self.account.id,
                                                                            type='test',
                                                                            amount=1)  # test, that changes will be applied on commit (but not on start)
        self.task.data['transaction_id'] = transaction_id

        self.assertEqual(game_tt_services.energy.cmd_balance(self.account.id), energy)

        self.assertEqual(self.task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(self.task.state, game_postponed_tasks.ComplexChangeTask.STATE.PROCESSED)

        time.sleep(0.1)

        self.assertEqual(game_tt_services.energy.cmd_balance(self.account.id), energy + 1)
