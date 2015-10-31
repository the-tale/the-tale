# coding: utf-8
import mock
import datetime

from the_tale.common.utils.testcase import TestCase
from the_tale.common.postponed_tasks import FakePostpondTaskPrototype, POSTPONED_TASK_LOGIC_RESULT

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.heroes import logic as heroes_logic

from the_tale.game.abilities.postponed_tasks import UseAbilityTask
from the_tale.game.abilities.relations import ABILITY_TYPE


class UseAbilityTasksTests(TestCase):

    def setUp(self):
        super(UseAbilityTasksTests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')

        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.task = UseAbilityTask(processor_id=ABILITY_TYPE.HELP.value,
                                   hero_id=self.hero.id,
                                   data={'hero_id': self.hero.id})

    def test_create(self):
        self.assertEqual(self.task.state, ComplexChangeTask.STATE.UNPROCESSED)

    def test_serialization(self):
        self.assertEqual(self.task.serialize(), UseAbilityTask.deserialize(self.task.serialize()).serialize())

    def test_response_data(self):
        self.assertEqual(self.task.processed_data, {})

    def test_banned(self):
        self.hero.ban_state_end_at = datetime.datetime.now() + datetime.timedelta(days=1)
        heroes_logic.save_hero(self.hero)
        self.assertEqual(self.task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(self.task.state, ComplexChangeTask.STATE.BANNED)

    def test_process_no_energy(self):
        self.hero.energy = 0
        self.hero.energy_bonus = 0
        heroes_logic.save_hero(self.hero)
        self.assertEqual(self.task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(self.task.state, ComplexChangeTask.STATE.HERO_CONDITIONS_NOT_PASSED)

    def test_process_can_not_process(self):

        with mock.patch('the_tale.game.abilities.deck.help.Help.use', lambda self, task, storage, pvp_balancer, highlevel: (ComplexChangeTask.RESULT.FAILED, None, ())):
            self.assertEqual(self.task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
            self.assertEqual(self.task.state, ComplexChangeTask.STATE.CAN_NOT_PROCESS)

    def test_process_success(self):
        self.assertEqual(self.task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(self.task.state, ComplexChangeTask.STATE.PROCESSED)

    def test_process_second_step_success(self):

        with mock.patch('the_tale.game.abilities.deck.help.Help.use', lambda self, task, storage, pvp_balancer, highlevel: (ComplexChangeTask.RESULT.CONTINUE, ComplexChangeTask.STEP.HIGHLEVEL, ())):
            self.assertEqual(self.task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        self.assertTrue(self.task.step.is_HIGHLEVEL)
        self.assertEqual(self.task.state, ComplexChangeTask.STATE.UNPROCESSED)

        self.assertEqual(self.task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(self.task.state, ComplexChangeTask.STATE.PROCESSED)


    def test_process_second_step_error(self):

        with mock.patch('the_tale.game.abilities.deck.help.Help.use', lambda self, task, storage, pvp_balancer, highlevel: (ComplexChangeTask.RESULT.CONTINUE, ComplexChangeTask.STEP.HIGHLEVEL, ())):
            self.assertEqual(self.task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        self.assertTrue(self.task.step.is_HIGHLEVEL)
        self.assertEqual(self.task.state, ComplexChangeTask.STATE.UNPROCESSED)

        with mock.patch('the_tale.game.abilities.deck.help.Help.use', lambda self, task, storage, pvp_balancer, highlevel: (ComplexChangeTask.RESULT.FAILED, None, ())):
            self.assertEqual(self.task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)

        self.assertEqual(self.task.state, ComplexChangeTask.STATE.CAN_NOT_PROCESS)
