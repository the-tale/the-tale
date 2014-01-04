# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user

from the_tale.game.text_generation import get_dictionary

from the_tale.game.heroes.prototypes import HeroPrototype

from the_tale.game.logic import create_test_map
from the_tale.game.prototypes import TimePrototype
from the_tale.game.logic_storage import LogicStorage
from the_tale.game.relations import RACE

from the_tale.game.map.places.relations import CITY_MODIFIERS

class GameTest(testcase.TestCase):

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

    def test_city_modifiers_in_dictionary(self):

        for modifier in CITY_MODIFIERS.records:
            self.assertTrue(modifier.text.lower() in get_dictionary())

    def test_race_in_dictionary(self):

        for race in RACE.records:
            self.assertTrue(race.text.lower() in get_dictionary())
