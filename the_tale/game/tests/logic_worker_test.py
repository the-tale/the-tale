# coding: utf-8
from django.test import TestCase
from dext.settings import settings

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.heroes.prototypes import HeroPrototype

from game.logic import create_test_map
from game.workers.environment import workers_environment
from game.prototypes import TimePrototype
from game.logic_storage import LogicStorage

class LogicTest(TestCase):

    def setUp(self):
        settings.refresh()

        self.p1, self.p2, self.p3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)
        self.action_idl = self.storage.heroes_to_actions[self.hero.id][-1]

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
        self.worker.process_mark_hero_as_not_fast(self.hero.id)
        self.assertFalse(self.worker.storage.heroes[self.hero.id].is_fast)
