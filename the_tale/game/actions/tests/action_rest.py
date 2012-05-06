# coding: utf-8

from django.test import TestCase

from game.logic import create_test_bundle, create_test_map, test_bundle_save
from game.actions.prototypes import ActionRestPrototype

class RestActionTest(TestCase):

    def setUp(self):
        create_test_map()

        self.bundle = create_test_bundle('RestActionTest')
        self.action_idl = self.bundle.tests_get_last_action()
        self.bundle.add_action(ActionRestPrototype.create(self.action_idl))
        self.action_rest = self.bundle.tests_get_last_action()
        self.hero = self.bundle.tests_get_hero()

    def tearDown(self):
        pass


    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_rest.leader, True)
        test_bundle_save(self, self.bundle)

    def test_processed(self):
        self.bundle.process_turn(1)
        self.assertEqual(len(self.bundle.actions), 1)
        self.assertEqual(self.bundle.tests_get_last_action(), self.action_idl)
        test_bundle_save(self, self.bundle)

    def test_not_ready(self):
        self.hero.health = 1
        self.bundle.process_turn(1)
        self.assertEqual(len(self.bundle.actions), 2)
        self.assertEqual(self.bundle.tests_get_last_action(), self.action_rest)
        self.assertTrue(self.hero.health > 1)
        test_bundle_save(self, self.bundle)

    def test_full_heal(self):
        self.hero.health = 1

        for i in xrange(self.hero.max_health):
            self.bundle.process_turn(i+1)
            if self.hero.health == self.hero.max_health:
                break

        self.assertEqual(self.hero.health, self.hero.max_health)
        test_bundle_save(self, self.bundle)
