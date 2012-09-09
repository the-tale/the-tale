# coding: utf-8
import mock

from django.test import TestCase

from dext.settings import settings

from game.balance import constants as c
from game.logic import create_test_bundle, create_test_map, test_bundle_save
from game.actions.prototypes import ActionDoNothingPrototype
from game.abilities.deck.help import Help
from game.prototypes import TimePrototype
from game.angels.prototypes import AngelPrototype

class DoNothingActionTest(TestCase):

    @mock.patch('game.actions.prototypes.ActionPrototype.get_description', lambda self: 'abrakadabra')
    def setUp(self):
        settings.refresh()

        create_test_map()

        self.bundle = create_test_bundle('RestActionTest')
        self.action_idl = self.bundle.tests_get_last_action()
        self.action_donothing = ActionDoNothingPrototype.create(self.action_idl, duration=7, messages_prefix='abrakadabra', messages_probability=0.3)
        self.hero = self.bundle.tests_get_hero()
        self.angel = AngelPrototype.get_by_id(self.hero.angel_id)

    def tearDown(self):
        pass

    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_donothing.leader, True)
        self.assertEqual(self.action_donothing.textgen_id, 'abrakadabra')
        self.assertEqual(self.action_donothing.percents_barier, 7)
        self.assertEqual(self.action_donothing.extra_probability, 0.3)
        test_bundle_save(self, self.bundle)

    def test_not_ready(self):
        self.bundle.process_turn()
        self.assertEqual(len(self.bundle.actions), 2)
        self.assertEqual(self.bundle.tests_get_last_action(), self.action_donothing)
        test_bundle_save(self, self.bundle)

    def test_full(self):

        current_time = TimePrototype.get_current_time()

        for i in xrange(7):
            self.assertEqual(len(self.bundle.actions), 2)
            self.assertTrue(self.action_donothing.leader)
            self.bundle.process_turn()
            current_time.increment_turn()

        self.assertEqual(len(self.bundle.actions), 1)
        self.assertTrue(self.action_idl.leader)

        test_bundle_save(self, self.bundle)
