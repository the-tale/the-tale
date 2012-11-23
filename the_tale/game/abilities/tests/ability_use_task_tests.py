# coding: utf-8
import mock

from dext.settings import settings

from common.utils.testcase import TestCase
from common.postponed_tasks import FakePostpondTaskPrototype

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.logic_storage import LogicStorage
from game.logic import create_test_map

from game.abilities.postponed_tasks import UseAbilityTask, ABILITY_TASK_STATE
from game.abilities.deck.help import Help

class UseAbilityTasksTests(TestCase):

    def setUp(self):
        settings.refresh()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')

        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.task = UseAbilityTask(ability_type=Help.get_type(),
                                   hero_id=self.hero.id,
                                   activated_at=0,
                                   available_at=666,
                                   data={'hero_id': self.hero.id})

    def test_create(self):
        self.assertEqual(self.task.state, ABILITY_TASK_STATE.UNPROCESSED)

    def test_serialization(self):
        self.assertEqual(self.task, UseAbilityTask.deserialize(self.task.serialize()))

    def test_response_data(self):
        self.assertEqual(self.task.response_data, {'available_at': 666})

    def test_process_no_energy(self):
        self.hero.model.energy = 0
        self.hero.save()
        self.assertFalse(self.task.process(FakePostpondTaskPrototype(), self.storage))
        self.assertTrue(self.task.state == ABILITY_TASK_STATE.NO_ENERGY)

    def test_process_cooldown(self):
        with mock.patch('game.abilities.deck.help.Help.available_at', 1):
            self.assertFalse(self.task.process(FakePostpondTaskPrototype(), self.storage))
            self.assertTrue(self.task.state == ABILITY_TASK_STATE.COOLDOWN)

    def test_process_can_not_process(self):

        with mock.patch('game.abilities.deck.help.Help.use', lambda self, storage, hero, data: False):
            self.assertFalse(self.task.process(FakePostpondTaskPrototype(), self.storage))
            self.assertTrue(self.task.state == ABILITY_TASK_STATE.CAN_NOT_PROCESS)

    def test_process_success(self):
        self.assertTrue(self.task.process(FakePostpondTaskPrototype(), self.storage))
        self.assertTrue(self.task.state == ABILITY_TASK_STATE.PROCESSED)
