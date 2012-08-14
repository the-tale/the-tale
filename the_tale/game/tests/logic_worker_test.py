# coding: utf-8
import mock

from django.test import TestCase

from dext.settings import settings

from game.angels.prototypes import AngelPrototype

from game.persons.storage import persons_storage
from game.persons.models import Person, PERSON_STATE

from game.map.places.storage import places_storage

from game.balance import constants as c
from game.logic import create_test_bundle, create_test_map
from game.workers.environment import workers_environment
from game.prototypes import TimePrototype

class LogicTest(TestCase):

    def setUp(self):
        self.p1, self.p2, self.p3 = create_test_map()

        self.bundle = create_test_bundle('HeroTest')
        self.action_idl = self.bundle.tests_get_last_action()
        self.hero = self.bundle.tests_get_hero()

        self.account = AngelPrototype.get_by_id(self.hero.angel_id).get_account()

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
        self.assertEqual(self.worker.bundles, {})
        self.assertEqual(self.worker.queue, [])
        self.assertEqual(self.worker.angels2bundles, {})
        self.assertEqual(self.worker.heroes2bundles, {})

    def test_process_mark_hero_as_not_fast(self):

        self.account.is_fast = True
        self.account.save()

        self.worker.process_register_bundle(self.bundle.id)
        self.assertTrue(self.worker.bundles[self.worker.heroes2bundles[self.hero.id]].heroes[self.hero.id].is_fast)
        self.worker.process_mark_hero_as_not_fast(self.hero.id)
        self.assertFalse(self.worker.bundles[self.worker.heroes2bundles[self.hero.id]].heroes[self.hero.id].is_fast)

    def test_process_register_bundle(self):

        self.assertTrue(self.hero.is_fast)

        self.worker.process_register_bundle(self.bundle.id)
        self.assertTrue(self.bundle.id in self.worker.bundles)
        self.assertEqual(self.worker.heroes2bundles[self.hero.id], self.bundle.id)
        self.assertEqual(self.worker.angels2bundles[self.hero.angel_id], self.bundle.id)

        self.assertFalse(self.worker.bundles[self.worker.heroes2bundles[self.hero.id]].heroes[self.hero.id].is_fast)
