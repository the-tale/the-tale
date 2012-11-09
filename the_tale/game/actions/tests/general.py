# coding: utf-8
import mock

from django.test import TestCase

from accounts.logic import register_user
from game.heroes.prototypes import HeroPrototype
from game.logic_storage import LogicStorage

from game.balance import constants as c
from game.logic import create_test_map
from game.prototypes import TimePrototype

from game.heroes.logic import create_mob_for_hero

from game.actions.prototypes import ACTION_TYPES, ActionBattlePvE1x1Prototype

class GeneralTest(TestCase):

    def setUp(self):
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)
        self.action_idl = self.storage.heroes_to_actions[self.hero.id][-1]

    def tearDown(self):
        pass

    def test_EXTRA_HELP_CHOICES(self):
        for action_class in ACTION_TYPES.values():
            self.assertTrue('EXTRA_HELP_CHOICES' in action_class.__dict__)

    def test_TEXTGEN_TYPE(self):
        for action_class in ACTION_TYPES.values():
            self.assertTrue('TEXTGEN_TYPE' in action_class.__dict__)

    def test_get_help_choice_has_heal(self):
        self.hero.health = 1

        heal_found = False
        for i in xrange(100):
            heal_found = heal_found or (self.action_idl.get_help_choice() == c.HELP_CHOICES.HEAL)

        self.assertTrue(heal_found)

    def check_heal_in_choices(self, result):
        heal_found = False
        for i in xrange(100):
            heal_found = heal_found or (self.action_idl.get_help_choice() == c.HELP_CHOICES.HEAL)

        self.assertEqual(heal_found, result)

    @mock.patch('game.actions.prototypes.ActionIdlenessPrototype.EXTRA_HELP_CHOICES', set())
    def test_help_choice_has_heal_for_full_health_without_alternative(self):
        self.check_heal_in_choices(False)

    def test_help_choice_has_heal_for_full_health_with_alternative(self):
        ActionBattlePvE1x1Prototype.create(self.action_idl, mob=create_mob_for_hero(self.hero))
        self.check_heal_in_choices(False)

    @mock.patch('game.actions.prototypes.ActionIdlenessPrototype.EXTRA_HELP_CHOICES', set())
    def test_help_choice_has_heal_for_large_health_without_alternative(self):
        self.hero.health = self.hero.max_health - 1
        self.check_heal_in_choices(True)

    def test_help_choice_has_heal_for_large_health_with_alternative(self):
        ActionBattlePvE1x1Prototype.create(self.action_idl, mob=create_mob_for_hero(self.hero))
        self.hero.health = self.hero.max_health - 1
        self.check_heal_in_choices(False)

    @mock.patch('game.actions.prototypes.ActionIdlenessPrototype.EXTRA_HELP_CHOICES', set())
    def test_help_choice_has_heal_for_low_health_without_alternative(self):
        self.hero.health = 1
        self.check_heal_in_choices(True)

    def test_help_choice_has_heal_for_low_health_with_alternative(self):
        ActionBattlePvE1x1Prototype.create(self.action_idl, mob=create_mob_for_hero(self.hero))
        self.hero.health = 1
        self.check_heal_in_choices(True)

    def test_percents_consistency(self):
        current_time = TimePrototype.get_current_time()

        # just test that quest will be ended
        while not self.action_idl.leader:
            self.storage.process_turn()
            current_time.increment_turn()
            self.assertEqual(self.storage.tests_get_last_action().percents, self.hero.last_action_percents)

    def test_help_choice_heal_not_in_choices_for_dead_hero(self):

        self.hero.health = 1
        self.hero.save()

        self.assertTrue(c.HELP_CHOICES.HEAL in self.action_idl.help_choices)

        self.hero.kill()
        self.hero.save()

        self.assertFalse(c.HELP_CHOICES.HEAL in self.action_idl.help_choices)
