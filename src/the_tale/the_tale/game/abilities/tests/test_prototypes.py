
import smart_imports

smart_imports.all()


ABILITY_TASK_STATE = game_postponed_tasks.ComplexChangeTask


class PrototypesTests(utils_testcase.TestCase):

    def setUp(self):
        super(PrototypesTests, self).setUp()
        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account.id)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.ability = deck.ABILITIES[relations.ABILITY_TYPE.HELP]()

        self.task_data = {}

    def test_activate__no_energy(self):
        energy = game_tt_services.energy.cmd_balance(self.account.id)
        game_tt_services.energy.cmd_change_balance(account_id=self.account.id,
                                                   type='test',
                                                   amount=-energy,
                                                   autocommit=True)

        task = self.ability.activate(self.hero, self.task_data)
        self.assertEqual(task, None)

    def test_activate__has_energy(self):
        task = self.ability.activate(self.hero, self.task_data)
        self.assertNotEqual(task.internal_logic.data['transaction_id'], None)

    @mock.patch('the_tale.game.abilities.relations.ABILITY_TYPE.HELP.cost', 0)
    def test_activate_and_complete__zero_cost(self):
        energy = game_tt_services.energy.cmd_balance(self.account.id)
        game_tt_services.energy.cmd_change_balance(account_id=self.account.id,
                                                   type='test',
                                                   amount=-energy,
                                                   autocommit=True)

        task = self.ability.activate(self.hero, self.task_data)
        self.assertEqual(task.internal_logic.data['transaction_id'], None)

        task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), storage=self.storage)

        self.assertTrue(task.state.is_processed)

        self.assertEqual(game_tt_services.energy.cmd_balance(self.account.id), 0)

    def test_activate_and_complete(self):
        energy = game_tt_services.energy.cmd_balance(self.account.id)

        task = self.ability.activate(self.hero, self.task_data)
        self.assertNotEqual(task.internal_logic.data['transaction_id'], None)

        self.assertEqual(game_tt_services.energy.cmd_balance(self.account.id), energy - self.ability.TYPE.cost)

        task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), storage=self.storage)

        self.assertTrue(task.state.is_processed)

        self.assertEqual(game_tt_services.energy.cmd_balance(self.account.id), energy - self.ability.TYPE.cost)
