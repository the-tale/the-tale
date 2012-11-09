# coding: utf-8
import itertools

import pymorphy

from django.test import TestCase

from textgen import words
from textgen.conf import textgen_settings

from game.artifacts.storage import ArtifactsDatabase
from game.mobs.storage import MobsDatabase

from accounts.logic import register_user

from game.text_generation import get_dictionary

from game.heroes.prototypes import HeroPrototype

from game import expected_values
from game.logic import create_test_map
from game.prototypes import TimePrototype
from game.logic_storage import LogicStorage

morph = pymorphy.get_morph(textgen_settings.PYMORPHY_DICTS_DIRECTORY)

class GameTest(TestCase):

    def test_mobs_loot_consistency(self):

        for mob_record in MobsDatabase.storage().data.values():
            for artifact_name in itertools.chain(mob_record.loot, mob_record.artifacts):
                self.assertTrue(artifact_name in ArtifactsDatabase.storage().data)

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


    def test_vocabulary_consistency(self):

        dictionary = get_dictionary()

        for mob_record in MobsDatabase.storage().data.values():
            word = dictionary.get_word(mob_record.normalized_name)
            self.assertTrue(not isinstance(word, words.Fake))

        for artifact_record in ArtifactsDatabase.storage().data.values():
            word = dictionary.get_word(artifact_record.normalized_name)
            self.assertTrue(not isinstance(word, words.Fake))

    def test_items_consitency(self):
        real_artifacts_list = set(ArtifactsDatabase.storage().data.keys())
        self.assertEqual(real_artifacts_list, expected_values.artifacts_list)

    def test_mobs_consitency(self):
        real_mobs_list = set(MobsDatabase.storage().data.keys())
        self.assertEqual(real_mobs_list, expected_values.mobs_list)
