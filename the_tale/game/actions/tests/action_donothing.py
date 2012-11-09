# coding: utf-8
import mock

from django.test import TestCase

from dext.settings import settings

from accounts.logic import register_user

from game.heroes.prototypes import HeroPrototype

from game.logic import create_test_map
from game.logic_storage import LogicStorage
from game.actions.prototypes import ActionDoNothingPrototype
from game.prototypes import TimePrototype


class DoNothingActionTest(TestCase):

    @mock.patch('game.actions.prototypes.ActionPrototype.get_description', lambda self: 'abrakadabra')
    def setUp(self):
        settings.refresh()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)
        self.action_idl = self.storage.heroes_to_actions[self.hero.id][-1]

        self.action_donothing = ActionDoNothingPrototype.create(self.action_idl, duration=7, messages_prefix='abrakadabra', messages_probability=0.3)


    def tearDown(self):
        pass

    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_donothing.leader, True)
        self.assertEqual(self.action_donothing.textgen_id, 'abrakadabra')
        self.assertEqual(self.action_donothing.percents_barier, 7)
        self.assertEqual(self.action_donothing.extra_probability, 0.3)
        self.storage._test_save()

    def test_not_ready(self):
        self.storage.process_turn()
        self.assertEqual(len(self.storage.actions), 2)
        self.assertEqual(self.storage.heroes_to_actions[self.hero.id][-1], self.action_donothing)
        self.storage._test_save()

    def test_full(self):

        current_time = TimePrototype.get_current_time()

        for i in xrange(7):
            self.assertEqual(len(self.storage.actions), 2)
            self.assertTrue(self.action_donothing.leader)
            self.storage.process_turn()
            current_time.increment_turn()

        self.assertEqual(len(self.storage.actions), 1)
        self.assertTrue(self.action_idl.leader)

        self.storage._test_save()
