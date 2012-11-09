# coding: utf-8

from django.test import TestCase

from accounts.logic import register_user
from game.heroes.prototypes import HeroPrototype

from game.logic import create_test_map

from game.heroes.habilities import nonbattle


class HabilitiesNonBattleTest(TestCase):

    def setUp(self):
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')
        self.hero = HeroPrototype.get_by_account_id(account_id)

    def tearDown(self):
        pass

    def test_charisma(self):
        self.assertTrue(100 < nonbattle.CHARISMA.update_quest_reward(self.hero, 100))

    def test_hackster(self):
        self.assertTrue(100 > nonbattle.HUCKSTER.update_buy_price(self.hero, 100))
        self.assertTrue(100 < nonbattle.HUCKSTER.update_sell_price(self.hero, 100))
