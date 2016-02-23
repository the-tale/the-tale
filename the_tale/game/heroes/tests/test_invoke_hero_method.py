# coding: utf-8
from the_tale.common.utils.testcase import TestCase
from the_tale.common.postponed_tasks.prototypes import POSTPONED_TASK_LOGIC_RESULT
from the_tale.common.postponed_tasks.tests.helpers import FakePostpondTaskPrototype

from the_tale.game.logic import create_test_map
from the_tale.game.logic_storage import LogicStorage

from the_tale.game.heroes.postponed_tasks import InvokeHeroMethodTask


class InvokeHeroMethodTaskTest(TestCase):

    def setUp(self):
        super(InvokeHeroMethodTaskTest, self).setUp()
        create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)

        self.hero = self.storage.accounts_to_heroes[self.account.id]


    def test_create(self):
        task = InvokeHeroMethodTask(self.hero.id, method_name='some_method', method_kwargs={'x': 'y', 'z': 0})
        self.assertTrue(task.state.is_UNPROCESSED)
        self.assertTrue(task.hero_id, self.hero.id)
        self.assertTrue(task.method_name, 'some_method')
        self.assertTrue(task.method_kwargs, {'x': 'y', 'z': 0})


    def test_serialization(self):
        task = InvokeHeroMethodTask(self.hero.id, method_name='some_method', method_kwargs={'x': 'y', 'z': 0})
        self.assertEqual(task.serialize(), InvokeHeroMethodTask.deserialize(task.serialize()).serialize())


    def test__can_not_found_method(self):
        task = InvokeHeroMethodTask(self.hero.id, method_name='missed_method', method_kwargs={'x': 'y', 'z': 0})

        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)

        self.assertTrue(task.state.is_METHOD_NOT_FOUND)


    def test_success(self):
        with self.check_delta(lambda: self.hero.experience, 66):
            task = InvokeHeroMethodTask(self.hero.id, method_name='add_experience', method_kwargs={'value': 66, 'without_modifications': True})

            self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

            self.assertTrue(task.state.is_PROCESSED)
