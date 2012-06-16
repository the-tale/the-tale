# coding: utf-8

from django.test import TestCase

from game.logic import create_test_bundle, create_test_map, test_bundle_save
from game.actions.prototypes import ActionQuestPrototype
from game.quests.logic import create_random_quest_for_hero
from game.prototypes import TimePrototype

class QuestActionTest(TestCase):

    def setUp(self):
        create_test_map()

        self.bundle = create_test_bundle('QuestActionTest')
        self.hero = self.bundle.tests_get_hero()
        self.action_idl = self.bundle.tests_get_last_action()
        self.quest = create_random_quest_for_hero(TimePrototype.get_current_time(), self.hero)
        self.bundle.add_action(ActionQuestPrototype.create(self.action_idl, TimePrototype.get_current_time(), quest=self.quest))
        self.action_quest = self.bundle.tests_get_last_action()

    def tearDown(self):
        pass


    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_quest.leader, True)
        test_bundle_save(self, self.bundle)

    def test_one_step(self):
        self.bundle.process_turn(TimePrototype.get_current_time())
        # quest can create new action on first step
        self.assertTrue(2 <= len(self.bundle.actions) <= 3)
        test_bundle_save(self, self.bundle)


    def test_full_quest(self):

        current_time = TimePrototype.get_current_time()

        # just test that quest will be ended
        while not self.action_idl.leader:
            self.bundle.process_turn(current_time)
            current_time.increment_turn()

        test_bundle_save(self, self.bundle)
