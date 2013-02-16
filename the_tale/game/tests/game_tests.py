# coding: utf-8

import pymorphy

from django.test import TestCase

from textgen.conf import textgen_settings

from accounts.logic import register_user

from game.text_generation import get_dictionary

from game.heroes.prototypes import HeroPrototype

from game.logic import create_test_map
from game.prototypes import TimePrototype
from game.logic_storage import LogicStorage

morph = pymorphy.get_morph(textgen_settings.PYMORPHY_DICTS_DIRECTORY)

class GameTest(TestCase):

    def test_dictionary_consistency(self):
        dictionary = get_dictionary()
        self.assertEqual(len(dictionary.get_undefined_words()), 0)

    def test_statistics_consistency(self):

        create_test_map()

        result, account_id, bundle_id = register_user('test_user')
        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)

        current_time = TimePrototype.get_current_time()

        for i in xrange(10000):
            self.storage.process_turn()
            current_time.increment_turn()

        self.assertEqual(self.hero.money, self.hero.statistics.money_earned - self.hero.statistics.money_spend)
