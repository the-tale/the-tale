# coding: utf-8
import mock

from dext.settings import settings

from common.utils.testcase import TestCase, CallCounter

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.heroes.prototypes import HeroPrototype

from game.models import SupervisorTask
from game.logic import create_test_map
from game.workers.environment import workers_environment
from game.logic_storage import LogicStorage
from game.prototypes import SupervisorTaskPrototype
from game.workers.supervisor import SupervisorException

from game.pvp.prototypes import Battle1x1Prototype


@mock.patch('game.workers.supervisor.Worker.wait_answers_from', lambda self, name, workers: None)
class SupervisorWorkerTests(TestCase):

    def setUp(self):
        settings.refresh()

        self.p1, self.p2, self.p3 = create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        result, account_2_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')

        self.hero = HeroPrototype.get_by_account_id(account_1_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)
        self.action_idl = self.storage.heroes_to_actions[self.hero.id][-1]

        self.account_1 = AccountPrototype.get_by_id(account_1_id)
        self.account_2 = AccountPrototype.get_by_id(account_2_id)

        workers_environment.deinitialize()
        workers_environment.initialize()

        self.worker = workers_environment.supervisor

    def test_initialization(self):
        from game.abilities.models import AbilityTask, ABILITY_TASK_STATE
        from game.abilities.prototypes import AbilityTaskPrototype
        from game.abilities.deck.help import Help
        from game.heroes.models import ChoosePreferencesTask, ChooseAbilityTask, PREFERENCE_TYPE, CHOOSE_ABILITY_STATE, CHOOSE_PREFERENCES_STATE
        from game.heroes.prototypes import ChooseAbilityTaskPrototype
        from game.heroes.habilities.attributes import EXTRA_SLOW
        from game.heroes.preferences import ChoosePreferencesTaskPrototype

        AbilityTaskPrototype.create(Help.get_type(), self.hero.id, 0, 0, {})
        ChooseAbilityTaskPrototype.create(EXTRA_SLOW.TYPE, self.hero.id)
        ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.MOB, None)

        self.assertEqual(AbilityTask.objects.filter(state=ABILITY_TASK_STATE.WAITING).count(), 1)
        self.assertEqual(ChooseAbilityTask.objects.filter(state=CHOOSE_ABILITY_STATE.WAITING).count(), 1)
        self.assertEqual(ChoosePreferencesTask.objects.filter(state=CHOOSE_PREFERENCES_STATE.WAITING).count(), 1)

        self.worker.initialize()

        self.assertEqual(AbilityTask.objects.filter(state=ABILITY_TASK_STATE.WAITING).count(), 0)
        self.assertEqual(ChooseAbilityTask.objects.filter(state=CHOOSE_ABILITY_STATE.WAITING).count(), 0)
        self.assertEqual(ChoosePreferencesTask.objects.filter(state=CHOOSE_PREFERENCES_STATE.WAITING).count(), 0)

        self.assertEqual(AbilityTask.objects.filter(state=ABILITY_TASK_STATE.RESET).count(), 1)
        self.assertEqual(ChooseAbilityTask.objects.filter(state=CHOOSE_ABILITY_STATE.RESET).count(), 1)
        self.assertEqual(ChoosePreferencesTask.objects.filter(state=CHOOSE_PREFERENCES_STATE.RESET).count(), 1)

        self.assertEqual(self.worker.tasks, {})
        self.assertEqual(self.worker.accounts_for_tasks, {})
        self.assertTrue(self.worker.initialized)

    def test_register_task(self):
        self.worker.initialize()

        task = SupervisorTaskPrototype.create_arena_pvp_1x1(self.account_1, self.account_2)

        Battle1x1Prototype.create(self.account_1).set_enemy(self.account_2)
        Battle1x1Prototype.create(self.account_2).set_enemy(self.account_1)

        self.assertEqual(len(self.worker.tasks), 0)
        self.assertEqual(len(self.worker.accounts_for_tasks), 0)

        release_accounts_counter = CallCounter()

        with mock.patch('game.workers.logic.Worker.cmd_release_account', release_accounts_counter):
            self.worker.register_task(task, release_accounts=False)

        self.assertEqual(len(self.worker.tasks), 1)
        self.assertEqual(len(self.worker.accounts_for_tasks), 2)
        self.assertFalse(self.worker.tasks.values()[0].all_members_captured)

        self.worker.process_account_released(self.account_1.id)
        self.worker.process_account_released(self.account_2.id)

        self.assertEqual(self.worker.tasks.values(), [])

        self.assertEqual(release_accounts_counter.count, 0)

    def test_register_task_release_account(self):
        self.worker.initialize()

        task = SupervisorTaskPrototype.create_arena_pvp_1x1(self.account_1, self.account_2)

        release_accounts_counter = CallCounter()

        with mock.patch('game.workers.logic.Worker.cmd_release_account', release_accounts_counter):
            self.worker.register_task(task)

        self.assertEqual(release_accounts_counter.count, 2)


    def test_register_task_second_time(self):
        self.worker.initialize()

        task = SupervisorTaskPrototype.create_arena_pvp_1x1(self.account_1, self.account_2)

        self.worker.register_task(task)
        self.assertRaises(SupervisorException, self.worker.register_task, task)

    def test_register_two_tasks_requested_one_account(self):
        self.worker.initialize()

        task = SupervisorTaskPrototype.create_arena_pvp_1x1(self.account_1, self.account_2)
        task_2 = SupervisorTaskPrototype.create_arena_pvp_1x1(self.account_1, self.account_2)

        self.worker.register_task(task)

        self.assertRaises(SupervisorException, self.worker.register_task, task_2)

    def test_register_account_not_in_task(self):
        self.worker.initialize()
        result, account_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')

        task = SupervisorTaskPrototype.create_arena_pvp_1x1(self.account_1, self.account_2)
        self.worker.register_task(task)

        register_account_counter = CallCounter()

        with mock.patch('game.workers.logic.Worker.cmd_register_account', register_account_counter):
            self.worker.register_account(account_id)

        self.assertEqual(register_account_counter.count, 1)
        self.assertEqual(set(self.worker.accounts_for_tasks.keys()), set([self.account_1.id, self.account_2.id]))
        self.assertEqual(self.worker.tasks.values()[0].captured_members, set())

    def test_register_account_in_task(self):
        self.worker.initialize()
        task = SupervisorTaskPrototype.create_arena_pvp_1x1(self.account_1, self.account_2)
        self.worker.register_task(task)

        register_account_counter = CallCounter()

        with mock.patch('game.workers.logic.Worker.cmd_register_account', register_account_counter):
            self.worker.register_account(self.account_1.id)

        self.assertEqual(register_account_counter.count, 0)
        self.assertEqual(set(self.worker.accounts_for_tasks.keys()), set([self.account_1.id, self.account_2.id]))
        self.assertEqual(self.worker.tasks.values()[0].captured_members, set([self.account_1.id]))

    def test_register_account_last_in_task(self):
        self.worker.initialize()

        Battle1x1Prototype.create(self.account_1).set_enemy(self.account_2)
        Battle1x1Prototype.create(self.account_2).set_enemy(self.account_1)
        task = SupervisorTaskPrototype.create_arena_pvp_1x1(self.account_1, self.account_2)

        self.worker.register_task(task)

        register_account_counter = CallCounter()

        with mock.patch('game.workers.logic.Worker.cmd_register_account', register_account_counter):
            self.worker.register_account(self.account_1.id)
            self.worker.register_account(self.account_2.id)

        self.assertEqual(register_account_counter.count, 2)
        self.assertEqual(set(self.worker.accounts_for_tasks.keys()), set())
        self.assertEqual(self.worker.tasks.values(), [])
        self.assertEqual(SupervisorTask.objects.all().count(), 0)
