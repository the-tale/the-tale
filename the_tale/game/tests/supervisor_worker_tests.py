# coding: utf-8
import mock

from dext.settings import settings

from common.utils import testcase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.heroes.prototypes import HeroPrototype

from game.models import SupervisorTask
from game.logic import create_test_map
from game.workers.environment import workers_environment
from game.prototypes import SupervisorTaskPrototype
from game.workers.supervisor import SupervisorException

from game.pvp.prototypes import Battle1x1Prototype


@mock.patch('game.workers.supervisor.Worker.wait_answers_from', lambda self, name, workers: None)
class SupervisorWorkerTests(testcase.TestCase):

    def setUp(self):
        settings.refresh()

        self.p1, self.p2, self.p3 = create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        result, account_2_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')

        self.hero_1 = HeroPrototype.get_by_account_id(account_1_id)
        self.hero_2 = HeroPrototype.get_by_account_id(account_2_id)

        self.account_1 = AccountPrototype.get_by_id(account_1_id)
        self.account_2 = AccountPrototype.get_by_id(account_2_id)

        workers_environment.deinitialize()
        workers_environment.initialize()

        self.worker = workers_environment.supervisor

    def test_initialization(self):
        from common.postponed_tasks import PostponedTask, PostponedTaskPrototype, POSTPONED_TASK_STATE, FakePostponedInternalTask

        PostponedTaskPrototype.create(FakePostponedInternalTask())

        self.assertEqual(PostponedTask.objects.filter(state=POSTPONED_TASK_STATE.WAITING).count(), 1)

        self.worker.process_initialize()

        self.assertEqual(PostponedTask.objects.filter(state=POSTPONED_TASK_STATE.WAITING).count(), 0)
        self.assertEqual(PostponedTask.objects.filter(state=POSTPONED_TASK_STATE.RESETED).count(), 1)

        self.assertEqual(self.worker.tasks, {})
        self.assertEqual(self.worker.accounts_for_tasks, {})
        self.assertEqual(self.worker.accounts_owners, {self.account_1.id: 'logic', self.account_2.id: 'logic'})
        self.assertEqual(self.worker.accounts_queues, {})
        self.assertTrue(self.worker.initialized)

    def test_register_task(self):
        self.worker.process_initialize()

        task = SupervisorTaskPrototype.create_arena_pvp_1x1(self.account_1, self.account_2)

        battle_1 = Battle1x1Prototype.create(self.account_1)
        battle_1.set_enemy(self.account_2)
        battle_1.save()

        battle_2 = Battle1x1Prototype.create(self.account_2)
        battle_2.set_enemy(self.account_1)
        battle_2.save()

        self.assertEqual(len(self.worker.tasks), 0)
        self.assertEqual(len(self.worker.accounts_for_tasks), 0)

        with mock.patch('game.workers.logic.Worker.cmd_release_account') as release_accounts_counter:
            self.worker.register_task(task, release_accounts=True)

        self.assertEqual(len(self.worker.tasks), 1)
        self.assertEqual(len(self.worker.accounts_for_tasks), 2)
        self.assertFalse(self.worker.tasks.values()[0].all_members_captured)
        self.assertEqual(self.worker.accounts_owners, {self.account_1.id: None, self.account_2.id: None})
        self.assertEqual(self.worker.accounts_queues, {})

        self.worker.process_account_released(self.account_1.id)
        self.assertEqual(self.worker.accounts_owners, {self.account_1.id: 'supervisor', self.account_2.id: None})

        #test commands queue
        self.worker.process_set_might(self.account_1.id, self.hero_1.id, 0)
        self.worker.process_set_might(self.account_2.id, self.hero_2.id, 1)
        self.worker.process_set_might(self.account_1.id, self.hero_1.id, 2)
        self.assertEqual(self.worker.accounts_queues, { self.account_1.id: [('set_might', {'account_id': self.account_1.id, 'hero_id': self.hero_1.id, 'might': 0}),
                                                                            ('set_might', {'account_id': self.account_1.id, 'hero_id': self.hero_1.id, 'might': 2}),],
                                                        self.account_2.id: [('set_might', {'account_id': self.account_2.id, 'hero_id': self.hero_2.id, 'might': 1})]})

        self.worker.process_account_released(self.account_2.id)
        self.assertEqual(self.worker.accounts_owners, {self.account_1.id: 'logic', self.account_2.id: 'logic'})

        self.assertEqual(len(self.worker.tasks), 0)

        self.assertEqual(release_accounts_counter.call_count, 2)

    def test_register_task_release_account(self):
        self.worker.process_initialize()

        task = SupervisorTaskPrototype.create_arena_pvp_1x1(self.account_1, self.account_2)

        with mock.patch('game.workers.logic.Worker.cmd_release_account') as release_accounts_counter:
            self.worker.register_task(task)

        self.assertEqual(release_accounts_counter.call_count, 2)


    def test_register_task_second_time(self):
        self.worker.process_initialize()

        task = SupervisorTaskPrototype.create_arena_pvp_1x1(self.account_1, self.account_2)

        self.worker.register_task(task)
        self.assertRaises(SupervisorException, self.worker.register_task, task)

    def test_register_two_tasks_requested_one_account(self):
        self.worker.process_initialize()

        task = SupervisorTaskPrototype.create_arena_pvp_1x1(self.account_1, self.account_2)
        task_2 = SupervisorTaskPrototype.create_arena_pvp_1x1(self.account_1, self.account_2)

        self.worker.register_task(task)

        self.assertRaises(SupervisorException, self.worker.register_task, task_2)

    def test_register_account_not_in_task(self):
        self.worker.process_initialize()
        result, account_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')

        task = SupervisorTaskPrototype.create_arena_pvp_1x1(self.account_1, self.account_2)
        self.worker.register_task(task)

        # for test pending account cmd queue
        self.worker.accounts_queues[account_id] = [('set_might', {'account_id': self.account_1.id, 'hero_id': self.hero_1.id, 'might': 0}),
                                                   ('set_might', {'account_id': self.account_1.id, 'hero_id': self.hero_1.id, 'might': 2}),
                                                   ('set_might', {'account_id': self.account_1.id, 'hero_id': self.hero_1.id, 'might': 4}) ]

        with mock.patch('game.workers.logic.Worker.cmd_register_account') as register_account_counter:
            with mock.patch('game.workers.logic.Worker.cmd_set_might') as set_might_counter:
                self.worker.register_account(account_id)

        self.assertEqual(set_might_counter.call_count, 3)
        self.assertEqual(register_account_counter.call_count, 1)
        self.assertEqual(set(self.worker.accounts_for_tasks.keys()), set([self.account_1.id, self.account_2.id]))
        self.assertEqual(self.worker.tasks.values()[0].captured_members, set())

    def test_register_account_in_task(self):
        self.worker.process_initialize()
        task = SupervisorTaskPrototype.create_arena_pvp_1x1(self.account_1, self.account_2)
        self.worker.register_task(task)

        with mock.patch('game.workers.logic.Worker.cmd_register_account') as register_account_counter:
            self.worker.register_account(self.account_1.id)

        self.assertEqual(register_account_counter.call_count, 0)
        self.assertEqual(set(self.worker.accounts_for_tasks.keys()), set([self.account_1.id, self.account_2.id]))
        self.assertEqual(self.worker.tasks.values()[0].captured_members, set([self.account_1.id]))

    def test_register_account_last_in_task(self):
        self.worker.process_initialize()

        Battle1x1Prototype.create(self.account_1).set_enemy(self.account_2)
        Battle1x1Prototype.create(self.account_2).set_enemy(self.account_1)
        task = SupervisorTaskPrototype.create_arena_pvp_1x1(self.account_1, self.account_2)

        self.worker.register_task(task)

        with mock.patch('game.workers.logic.Worker.cmd_register_account') as register_account_counter:
            self.worker.register_account(self.account_1.id)
            self.worker.register_account(self.account_2.id)

        self.assertEqual(register_account_counter.call_count, 2)
        self.assertEqual(set(self.worker.accounts_for_tasks.keys()), set())
        self.assertEqual(self.worker.tasks.values(), [])
        self.assertEqual(SupervisorTask.objects.all().count(), 0)

    def test_dispatch_command_for_unregistered_account(self):
        self.worker.process_initialize()

        result, account_3_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')

        hero_3 = HeroPrototype.get_by_id(account_3_id)

        with mock.patch('game.workers.logic.Worker.cmd_logic_task') as logic_task_counter:
            with mock.patch.object(self.worker.logger, 'warn') as logger_warn_counter:
                self.worker.process_mark_hero_as_active(account_3_id, hero_3.id)

        self.assertEqual(logic_task_counter.call_count, 0)
        self.assertEqual(logger_warn_counter.call_count, 1)
        self.assertFalse(account_3_id in self.worker.accounts_owners)
        self.assertTrue(account_3_id in self.worker.accounts_queues)
