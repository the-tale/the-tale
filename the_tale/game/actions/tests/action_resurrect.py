# coding: utf-8

from django.test import TestCase

from game.logic import create_test_bundle, create_test_map, test_bundle_save
from game.actions.prototypes import ActionResurrectPrototype
from game.balance import constants as c
from game.prototypes import TimePrototype

class ResurrectActionTest(TestCase):

    def setUp(self):
        create_test_map()

        self.bundle = create_test_bundle('ResurrectActionTest')

        self.hero = self.bundle.tests_get_hero()
        self.hero.kill()

        self.action_idl = self.bundle.tests_get_last_action()
        self.bundle.add_action(ActionResurrectPrototype.create(self.action_idl, TimePrototype.get_current_time()))
        self.action_resurrect = self.bundle.tests_get_last_action()


    def tearDown(self):
        pass

    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_resurrect.leader, True)
        test_bundle_save(self, self.bundle)

    def test_processed(self):

        current_time = TimePrototype.get_current_time()

        for i in xrange(c.TURNS_TO_RESURRECT-1):

            self.bundle.process_turn(current_time)
            current_time.increment_turn()
            self.assertEqual(len(self.bundle.actions), 2)
            self.assertEqual(self.bundle.tests_get_last_action(), self.action_resurrect)

        self.bundle.process_turn(current_time)
        self.assertEqual(len(self.bundle.actions), 1)
        self.assertEqual(self.bundle.tests_get_last_action(), self.action_idl)

        self.assertEqual(self.hero.health, self.hero.max_health)
        self.assertEqual(self.hero.is_alive, True)

        test_bundle_save(self, self.bundle)


    def test_fast_resurrect(self):

        self.action_resurrect.fast_resurrect()

        self.bundle.process_turn(TimePrototype.get_current_time())
        self.assertEqual(len(self.bundle.actions), 1)
        self.assertEqual(self.bundle.tests_get_last_action(), self.action_idl)

        self.assertEqual(self.hero.health, self.hero.max_health)
        self.assertEqual(self.hero.is_alive, True)

        test_bundle_save(self, self.bundle)
