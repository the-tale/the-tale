# coding: utf-8

from django.test import TestCase

from dext.settings import settings

from accounts.logic import register_user
from game.heroes.prototypes import HeroPrototype
from game.logic_storage import LogicStorage

from game.logic import create_test_map
from game.actions.prototypes import ActionResurrectPrototype
from game.balance import constants as c
from game.prototypes import TimePrototype

class ResurrectActionTest(TestCase):

    def setUp(self):
        settings.refresh()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)
        self.action_idl = self.storage.heroes_to_actions[self.hero.id][-1]

        self.hero.kill()

        self.action_resurrect = ActionResurrectPrototype.create(self.action_idl)

    def tearDown(self):
        pass

    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_resurrect.leader, True)
        self.storage._test_save()

    def test_processed(self):

        current_time = TimePrototype.get_current_time()

        for i in xrange(c.TURNS_TO_RESURRECT-1):

            self.storage.process_turn()
            current_time.increment_turn()
            self.assertEqual(len(self.storage.actions), 2)
            self.assertEqual(self.storage.heroes_to_actions[self.hero.id][-1], self.action_resurrect)

        self.storage.process_turn()
        self.assertEqual(len(self.storage.actions), 1)
        self.assertEqual(self.storage.heroes_to_actions[self.hero.id][-1], self.action_idl)

        self.assertEqual(self.hero.health, self.hero.max_health)
        self.assertEqual(self.hero.is_alive, True)

        self.storage._test_save()

    def test_full(self):

        current_time = TimePrototype.get_current_time()

        while len(self.storage.actions) != 1:
            self.storage.process_turn()
            current_time.increment_turn()

        self.assertTrue(self.action_idl.leader)
        self.assertEqual(self.hero.health, self.hero.max_health)
        self.assertEqual(self.hero.is_alive, True)

        self.storage._test_save()

    def test_fast_resurrect(self):

        self.action_resurrect.fast_resurrect()

        self.storage.process_turn()
        self.assertEqual(len(self.storage.actions), 1)
        self.assertEqual(self.storage.heroes_to_actions[self.hero.id][-1], self.action_idl)

        self.assertEqual(self.hero.health, self.hero.max_health)
        self.assertEqual(self.hero.is_alive, True)

        self.storage._test_save()
