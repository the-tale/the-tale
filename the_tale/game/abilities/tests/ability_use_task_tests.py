# coding: utf-8
import mock
import datetime

from the_tale.common.utils.testcase import TestCase
from the_tale.common.postponed_tasks import FakePostpondTaskPrototype, POSTPONED_TASK_LOGIC_RESULT

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.abilities.postponed_tasks import UseAbilityTask, ABILITY_TASK_STATE
from the_tale.game.abilities.relations import ABILITY_TYPE, ABILITY_RESULT


class UseAbilityTasksTests(TestCase):

    def setUp(self):
        super(UseAbilityTasksTests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')

        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.task = UseAbilityTask(ability_type=ABILITY_TYPE.HELP,
                                   hero_id=self.hero.id,
                                   data={'hero_id': self.hero.id})

    def test_create(self):
        self.assertEqual(self.task.state, ABILITY_TASK_STATE.UNPROCESSED)

    def test_serialization(self):
        self.assertEqual(self.task.serialize(), UseAbilityTask.deserialize(self.task.serialize()).serialize())

    def test_response_data(self):
        self.assertEqual(self.task.processed_data, {})

    def test_banned(self):
        self.hero.ban_state_end_at = datetime.datetime.now() + datetime.timedelta(days=1)
        self.hero.save()
        self.assertEqual(self.task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(self.task.state, ABILITY_TASK_STATE.BANNED)

    def test_process_no_energy(self):
        self.hero._model.energy = 0
        self.hero.save()
        self.assertEqual(self.task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(self.task.state, ABILITY_TASK_STATE.NO_ENERGY)

    def test_process_bonus_energy(self):
        self.hero._model.energy = 0
        self.hero.add_energy_bonus(100)
        self.hero.save()
        self.assertEqual(self.task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(self.task.state, ABILITY_TASK_STATE.PROCESSED)

    def test_process_can_not_process(self):

        with mock.patch('the_tale.game.abilities.deck.help.Help.use', lambda self, data, step, main_task_id, storage, pvp_balancer, highlevel: (ABILITY_RESULT.FAILED, None, ())):
            self.assertEqual(self.task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
            self.assertEqual(self.task.state, ABILITY_TASK_STATE.CAN_NOT_PROCESS)

    def test_process_success(self):
        self.assertEqual(self.task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(self.task.state, ABILITY_TASK_STATE.PROCESSED)

    def test_process_second_step_success(self):

        with mock.patch('the_tale.game.abilities.deck.help.Help.use', lambda self, data, step, main_task_id, storage, pvp_balancer, highlevel: (ABILITY_RESULT.CONTINUE, 'second-step', ())):
            self.assertEqual(self.task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        self.assertEqual(self.task.step, 'second-step')
        self.assertEqual(self.task.state, ABILITY_TASK_STATE.UNPROCESSED)

        self.assertEqual(self.task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(self.task.state, ABILITY_TASK_STATE.PROCESSED)


    def test_process_second_step_error(self):

        with mock.patch('the_tale.game.abilities.deck.help.Help.use', lambda self, data, step, main_task_id, storage, pvp_balancer, highlevel: (ABILITY_RESULT.CONTINUE, 'second-step', ())):
            self.assertEqual(self.task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        self.assertEqual(self.task.step, 'second-step')
        self.assertEqual(self.task.state, ABILITY_TASK_STATE.UNPROCESSED)

        with mock.patch('the_tale.game.abilities.deck.help.Help.use', lambda self, data, step, main_task_id, storage, pvp_balancer, highlevel: (ABILITY_RESULT.FAILED, None, ())):
            self.assertEqual(self.task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)

        self.assertEqual(self.task.state, ABILITY_TASK_STATE.CAN_NOT_PROCESS)
