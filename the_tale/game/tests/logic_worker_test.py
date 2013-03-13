# coding: utf-8
import datetime
import mock

from common.utils import testcase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.heroes.prototypes import HeroPrototype

from game.logic import create_test_map
from game.workers.environment import workers_environment
from game.prototypes import TimePrototype


class LogicWorkerTests(testcase.TestCase):

    def setUp(self):
        super(LogicWorkerTests, self).setUp()

        self.p1, self.p2, self.p3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.account = AccountPrototype.get_by_id(self.hero.account_id)

        workers_environment.deinitialize()
        workers_environment.initialize()

        self.worker = workers_environment.logic
        self.worker.process_initialize(TimePrototype.get_current_turn_number(), 'logic')

    def tearDown(self):
        pass

    def test_process_initialize(self):
        self.assertTrue(self.worker.initialized)
        self.assertEqual(self.worker.worker_id, 'logic')
        self.assertEqual(self.worker.turn_number, 0)
        self.assertEqual(self.worker.storage.heroes, {})
        self.assertEqual(self.worker.storage.actions, {})
        self.assertEqual(self.worker.storage.heroes_to_actions, {})
        self.assertEqual(self.worker.queue, [])

    def test_process_mark_hero_as_not_fast(self):

        self.account.is_fast = True
        self.account.save()

        self.worker.process_register_account(self.account.id)
        self.assertTrue(self.worker.storage.heroes[self.hero.id].is_fast)
        self.worker.process_mark_hero_as_not_fast(self.hero.account_id, self.hero.id)
        self.assertFalse(self.worker.storage.heroes[self.hero.id].is_fast)

    def test_process_start_hero_caching(self):
        current_time = datetime.datetime.now()
        self.worker.process_register_account(self.account.id)
        self.assertTrue(self.worker.storage.heroes[self.hero.id].ui_caching_started_at < current_time)
        self.worker.process_start_hero_caching(self.account.id, self.hero.id)
        self.assertTrue(self.worker.storage.heroes[self.hero.id].ui_caching_started_at > current_time)


    def test_process_next_turn(self):

        current_time = TimePrototype.get_current_time()
        current_time.increment_turn()
        current_time.save()

        self.worker.process_register_account(self.account.id)

        with mock.patch('game.workers.supervisor.Worker.cmd_account_release_required') as release_required_counter:
            with mock.patch('game.heroes.prototypes.HeroPrototype.save') as save_counter:
                self.worker.process_next_turn(current_time.turn_number)

        self.assertEqual(save_counter.call_count, 1)
        self.assertEqual(release_required_counter.call_count, 0)


    def test_process_next_turn_with_skipped_hero(self):

        current_time = TimePrototype.get_current_time()
        current_time.increment_turn()
        current_time.save()

        self.worker.process_register_account(self.account.id)

        self.worker.storage.skipped_heroes.add(self.hero.id)

        with mock.patch('game.workers.supervisor.Worker.cmd_account_release_required') as release_required_counter:
            with mock.patch('game.heroes.prototypes.HeroPrototype.save') as save_counter:
                self.worker.process_next_turn(TimePrototype.get_current_turn_number())

        self.assertEqual(save_counter.call_count, 0)
        self.assertEqual(release_required_counter.call_count, 1)
