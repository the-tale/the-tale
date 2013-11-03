# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.heroes.prototypes import HeroPrototype

from the_tale.game.models import SupervisorTask
from the_tale.game.logic import create_test_map
from the_tale.game.workers.environment import workers_environment
from the_tale.game.prototypes import SupervisorTaskPrototype
from the_tale.game.workers.supervisor import SupervisorException

from the_tale.game.pvp.prototypes import Battle1x1Prototype

_wait_answers_state = 'logic' # for one specific test


@mock.patch('the_tale.game.workers.supervisor.Worker.wait_answers_from', lambda self, name, workers: None)
class SupervisorWorkerTests(testcase.TestCase):

    def setUp(self):
        super(SupervisorWorkerTests, self).setUp()

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

        self.worker.logger = mock.Mock()

    def test_initialization(self):
        from the_tale.common.postponed_tasks import PostponedTask, PostponedTaskPrototype, POSTPONED_TASK_STATE, FakePostponedInternalTask

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

        with mock.patch('the_tale.game.workers.logic.Worker.cmd_release_account') as release_accounts_counter:
            self.worker.register_task(task, release_accounts=True)

        self.assertEqual(len(self.worker.tasks), 1)
        self.assertEqual(len(self.worker.accounts_for_tasks), 2)
        self.assertFalse(self.worker.tasks.values()[0].all_members_captured)
        self.assertEqual(self.worker.accounts_owners, {self.account_1.id: None, self.account_2.id: None})
        self.assertEqual(self.worker.accounts_queues, {})

        self.worker.process_account_released(self.account_1.id)
        self.assertEqual(self.worker.accounts_owners, {self.account_1.id: 'supervisor', self.account_2.id: None})

        #test commands queue
        self.worker.process_start_hero_caching(self.account_1.id, self.hero_1.id)
        self.worker.process_start_hero_caching(self.account_2.id, self.hero_2.id)
        self.worker.process_logic_task(self.account_1.id, 666)
        self.assertEqual(self.worker.accounts_queues, { self.account_1.id: [('start_hero_caching', {'account_id': self.account_1.id, 'hero_id': self.hero_1.id}),
                                                                            ('logic_task', {'account_id': self.account_1.id, 'task_id': 666}),],
                                                        self.account_2.id: [('start_hero_caching', {'account_id': self.account_2.id, 'hero_id': self.hero_2.id})]})

        self.worker.process_account_released(self.account_2.id)
        self.assertEqual(self.worker.accounts_owners, {self.account_1.id: 'logic', self.account_2.id: 'logic'})

        self.assertEqual(len(self.worker.tasks), 0)

        self.assertEqual(release_accounts_counter.call_count, 2)

    def test_register_task_release_account(self):
        self.worker.process_initialize()

        task = SupervisorTaskPrototype.create_arena_pvp_1x1(self.account_1, self.account_2)

        with mock.patch('the_tale.game.workers.logic.Worker.cmd_release_account') as release_accounts_counter:
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

        self.assertTrue(self.worker.logger.calls_count > 0)

    def test_register_account_not_in_task(self):
        self.worker.process_initialize()
        result, account_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')

        task = SupervisorTaskPrototype.create_arena_pvp_1x1(self.account_1, self.account_2)
        self.worker.register_task(task)

        # for test pending account cmd queue
        self.worker.accounts_queues[account_id] = [('logic_task', {'account_id': self.account_1.id, 'task_id': 1}),
                                                   ('logic_task', {'account_id': self.account_1.id, 'task_id': 2}),
                                                   ('logic_task', {'account_id': self.account_1.id, 'task_id': 4}) ]

        with mock.patch('the_tale.game.workers.logic.Worker.cmd_register_account') as register_account_counter:
            with mock.patch('the_tale.game.workers.logic.Worker.cmd_logic_task') as cmd_logic_task:
                self.worker.register_account(account_id)

        self.assertEqual(cmd_logic_task.call_count, 3)
        self.assertEqual(register_account_counter.call_count, 1)
        self.assertEqual(set(self.worker.accounts_for_tasks.keys()), set([self.account_1.id, self.account_2.id]))
        self.assertEqual(self.worker.tasks.values()[0].captured_members, set())

    def test_register_account_in_task(self):
        self.worker.process_initialize()
        task = SupervisorTaskPrototype.create_arena_pvp_1x1(self.account_1, self.account_2)
        self.worker.register_task(task)

        with mock.patch('the_tale.game.workers.logic.Worker.cmd_register_account') as register_account_counter:
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

        with mock.patch('the_tale.game.workers.logic.Worker.cmd_register_account') as register_account_counter:
            self.worker.register_account(self.account_1.id)
            self.worker.register_account(self.account_2.id)

        self.assertEqual(register_account_counter.call_count, 2)
        self.assertEqual(set(self.worker.accounts_for_tasks.keys()), set())
        self.assertEqual(self.worker.tasks.values(), [])
        self.assertEqual(SupervisorTask.objects.all().count(), 0)

    def test_dispatch_command_for_unregistered_account(self):
        self.worker.process_initialize()

        result, account_3_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')

        account_3 = AccountPrototype.get_by_id(account_3_id)
        hero_3 = HeroPrototype.get_by_id(account_3_id)

        with mock.patch('the_tale.game.workers.logic.Worker.cmd_logic_task') as logic_task_counter:
            with mock.patch.object(self.worker.logger, 'warn') as logger_warn_counter:
                self.worker.process_update_hero_with_account_data(account_3_id,
                                                                  hero_3.id,
                                                                  is_fast=account_3.is_fast,
                                                                  premium_end_at=account_3.premium_end_at,
                                                                  active_end_at=account_3.active_end_at,
                                                                  ban_end_at=account_3.ban_game_end_at,
                                                                  might=666)

        self.assertEqual(logic_task_counter.call_count, 0)
        self.assertEqual(logger_warn_counter.call_count, 1)
        self.assertFalse(account_3_id in self.worker.accounts_owners)
        self.assertTrue(account_3_id in self.worker.accounts_queues)

    @mock.patch('the_tale.game.conf.game_settings.ENABLE_WORKER_HIGHLEVEL', True)
    def test_process_next_turn(self):
        self.worker.process_initialize()
        with mock.patch('the_tale.game.workers.supervisor.Worker.wait_answers_from') as wait_answers_from:
            self.worker.process_next_turn()

        self.assertEqual(wait_answers_from.call_count, 2)

    @mock.patch('the_tale.game.conf.game_settings.ENABLE_WORKER_HIGHLEVEL', True)
    @mock.patch('the_tale.game.workers.supervisor.Worker.logger.error', mock.Mock())
    def test_process_next_turn__timeout_in_highlevel(self):
        from the_tale.common.amqp_queues import exceptions as amqp_exceptions

        self.worker.process_initialize()


        def wait_answers_from(worker, code, workers=(), timeout=60.0):
            global _wait_answers_state
            if _wait_answers_state == 'logic':
                _wait_answers_state = 'highlevel'
                return
            if _wait_answers_state == 'highlevel':
                _wait_answers_state = 'stop'
                raise amqp_exceptions.WaitAnswerTimeoutError(code='code', workers='workers', timeout=60.0)

        with mock.patch('the_tale.game.workers.supervisor.Worker.wait_answers_from', wait_answers_from):
            with mock.patch('the_tale.game.workers.logic.Worker.cmd_stop') as logic_cmd_stop:
                self.assertRaises(amqp_exceptions.WaitAnswerTimeoutError, self.worker.process_next_turn)

        self.assertEqual(logic_cmd_stop.call_count, 1)
