
import smart_imports

smart_imports.all()


class InvokeHeroMethodTaskTest(utils_testcase.TestCase):

    def setUp(self):
        super(InvokeHeroMethodTaskTest, self).setUp()
        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account.id)

        self.hero = self.storage.accounts_to_heroes[self.account.id]

    def test_create(self):
        task = postponed_tasks.InvokeHeroMethodTask(self.hero.id, method_name='some_method', method_kwargs={'x': 'y', 'z': 0})
        self.assertTrue(task.state.is_UNPROCESSED)
        self.assertTrue(task.hero_id, self.hero.id)
        self.assertTrue(task.method_name, 'some_method')
        self.assertTrue(task.method_kwargs, {'x': 'y', 'z': 0})

    def test_serialization(self):
        task = postponed_tasks.InvokeHeroMethodTask(self.hero.id, method_name='some_method', method_kwargs={'x': 'y', 'z': 0})
        self.assertEqual(task.serialize(), postponed_tasks.InvokeHeroMethodTask.deserialize(task.serialize()).serialize())

    def test__can_not_found_method(self):
        task = postponed_tasks.InvokeHeroMethodTask(self.hero.id, method_name='missed_method', method_kwargs={'x': 'y', 'z': 0})

        self.assertEqual(task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)

        self.assertTrue(task.state.is_METHOD_NOT_FOUND)

    def test_success(self):
        with self.check_delta(lambda: self.hero.experience, 66):
            task = postponed_tasks.InvokeHeroMethodTask(self.hero.id, method_name='add_experience', method_kwargs={'value': 66, 'without_modifications': True})

            self.assertEqual(task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

            self.assertTrue(task.state.is_PROCESSED)
