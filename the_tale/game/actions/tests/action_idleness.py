# coding: utf-8

from django.test import TestCase

from game.logic import create_test_bundle, create_test_map, test_bundle_save
from game.actions.prototypes import ActionIdlenessPrototype, ActionQuestPrototype, ActionInPlacePrototype
from game.balance import constants as c
from game.prototypes import TimePrototype

class IdlenessActionTest(TestCase):

    def setUp(self):
        create_test_map()

        self.bundle = create_test_bundle('IdlenessActionTest')
        self.action_idl = self.bundle.tests_get_last_action()
        self.hero = self.bundle.tests_get_hero()

    def tearDown(self):
        pass


    def test_create(self):
        self.assertEqual(self.action_idl.leader, True)
        test_bundle_save(self, self.bundle)


    def test_first_quest(self):
        self.bundle.process_turn()
        self.assertEqual(len(self.bundle.actions), 2)
        self.assertEqual(self.bundle.tests_get_last_action().TYPE, ActionQuestPrototype.TYPE)
        self.assertEqual(self.action_idl.state, ActionIdlenessPrototype.STATE.QUEST)
        self.assertTrue(self.action_idl.updated)
        test_bundle_save(self, self.bundle)


    def test_inplace(self):
        self.action_idl.state = ActionIdlenessPrototype.STATE.QUEST
        self.bundle.process_turn()
        self.assertEqual(len(self.bundle.actions), 2)
        self.assertEqual(self.bundle.tests_get_last_action().TYPE, ActionInPlacePrototype.TYPE)
        self.assertEqual(self.action_idl.state, ActionIdlenessPrototype.STATE.IN_PLACE)
        test_bundle_save(self, self.bundle)

    def test_waiting(self):
        self.action_idl.state = ActionIdlenessPrototype.STATE.IN_PLACE
        self.bundle.process_turn()
        self.assertEqual(len(self.bundle.actions), 1)
        self.assertEqual(self.bundle.tests_get_last_action(), self.action_idl)
        self.assertEqual(self.action_idl.state, ActionIdlenessPrototype.STATE.WAITING)
        test_bundle_save(self, self.bundle)


    def test_full_waiting(self):
        self.action_idl.state = ActionIdlenessPrototype.STATE.WAITING
        self.action_idl.percents = 0

        current_time = TimePrototype.get_current_time()

        for i in xrange(c.TURNS_TO_IDLE-1):
            self.bundle.process_turn()
            current_time.increment_turn()
            self.assertEqual(len(self.bundle.actions), 1)
            self.assertEqual(self.bundle.tests_get_last_action(), self.action_idl)

        self.bundle.process_turn()

        self.assertEqual(len(self.bundle.actions), 2)
        self.assertEqual(self.bundle.tests_get_last_action().TYPE, ActionQuestPrototype.TYPE)
        self.assertEqual(self.action_idl.state, ActionIdlenessPrototype.STATE.QUEST)

        test_bundle_save(self, self.bundle)

    def test_initiate_quest(self):
        self.action_idl.state = ActionIdlenessPrototype.STATE.WAITING
        self.action_idl.percents = 0

        self.action_idl.init_quest()

        self.bundle.process_turn()

        self.assertEqual(len(self.bundle.actions), 2)
        self.assertEqual(self.bundle.tests_get_last_action().TYPE, ActionQuestPrototype.TYPE)
        self.assertEqual(self.action_idl.state, ActionIdlenessPrototype.STATE.QUEST)

        test_bundle_save(self, self.bundle)
