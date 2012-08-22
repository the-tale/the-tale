# coding: utf-8

from django.test import TestCase

from game.logic import create_test_bundle, create_test_map
from game.prototypes import TimePrototype

from game.actions.prototypes import ACTION_TYPES, HELP_CHOICES

class GeneralTest(TestCase):

    def setUp(self):
        create_test_map()

        self.bundle = create_test_bundle('IdlenessActionTest')
        self.action_idl = self.bundle.tests_get_last_action()
        self.hero = self.bundle.tests_get_hero()

    def tearDown(self):
        pass

    def test_EXTRA_HELP_CHOICES(self):
        for action_class in ACTION_TYPES.values():
            self.assertTrue('EXTRA_HELP_CHOICES' in action_class.__dict__)

    def test_TEXTGEN_TYPE(self):
        for action_class in ACTION_TYPES.values():
            self.assertTrue('TEXTGEN_TYPE' in action_class.__dict__)

    def test_get_help_choice_has_heal(self):
        for i in xrange(100):
            self.assertNotEqual(self.action_idl.get_help_choice(), HELP_CHOICES.HEAL)

        self.hero.health = 1

        heal_found = False
        for i in xrange(100):
            heal_found = heal_found or (self.action_idl.get_help_choice() == HELP_CHOICES.HEAL)

        self.assertTrue(heal_found)


    def test_percents_consistency(self):
        current_time = TimePrototype.get_current_time()

        # just test that quest will be ended
        while not self.action_idl.leader:
            self.bundle.process_turn()
            current_time.increment_turn()
            self.assertEqual(self.bundle.tests_get_last_action().percents, self.hero.last_action_percents)

    def test_help_choice_heal_not_in_choices_for_dead_hero(self):

        self.hero.health = 1
        self.hero.save()

        self.assertTrue(HELP_CHOICES.HEAL in self.action_idl.help_choices)

        self.hero.kill()
        self.hero.save()

        self.assertFalse(HELP_CHOICES.HEAL in self.action_idl.help_choices)
