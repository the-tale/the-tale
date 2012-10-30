# coding: utf-8
import mock

from django.test import TestCase

from dext.settings import settings

from game.balance import constants as c
from game.logic import create_test_bundle, create_test_map, test_bundle_save
from game.actions.prototypes import ActionRestPrototype
from game.abilities.deck.help import Help
from game.prototypes import TimePrototype

class RestActionTest(TestCase):

    def setUp(self):
        settings.refresh()

        create_test_map()

        self.bundle = create_test_bundle('RestActionTest')
        self.action_idl = self.bundle.tests_get_last_action()
        self.action_rest = ActionRestPrototype.create(self.action_idl)
        self.hero = self.bundle.tests_get_hero()

    def tearDown(self):
        pass


    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_rest.leader, True)
        test_bundle_save(self, self.bundle)

    def test_processed(self):
        self.bundle.process_turn()
        self.assertEqual(len(self.bundle.actions), 1)
        self.assertEqual(self.bundle.tests_get_last_action(), self.action_idl)
        test_bundle_save(self, self.bundle)

    def test_not_ready(self):
        self.hero.health = 1
        self.bundle.process_turn()
        self.assertEqual(len(self.bundle.actions), 2)
        self.assertEqual(self.bundle.tests_get_last_action(), self.action_rest)
        self.assertTrue(self.hero.health > 1)
        test_bundle_save(self, self.bundle)

    def test_ability_heal(self):

        ability = Help.get_by_hero_id(self.hero.id)

        self.hero.health = 1

        old_percents = self.action_rest.percents

        with mock.patch('game.actions.prototypes.ActionPrototype.get_help_choice', lambda x: c.HELP_CHOICES.HEAL):
            self.assertTrue(ability.use(self.bundle, self.hero, None))
            self.assertTrue(self.hero.health > 1)
            self.assertTrue(old_percents < self.action_rest.percents)
            self.assertEqual(self.hero.last_action_percents, self.action_rest.percents)

    def test_full(self):
        self.hero.health = 1

        current_time = TimePrototype.get_current_time()

        while len(self.bundle.actions) != 1:
            self.bundle.process_turn()
            current_time.increment_turn()

        self.assertTrue(self.action_idl.leader)
        self.assertEqual(self.hero.health, self.hero.max_health)

        test_bundle_save(self, self.bundle)
