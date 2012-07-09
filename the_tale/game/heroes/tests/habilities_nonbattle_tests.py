# coding: utf-8

from django.test import TestCase

from game.logic import create_test_map, create_test_bundle

from game.heroes.habilities import nonbattle


class HabilitiesNonBattleTest(TestCase):

    def setUp(self):
        create_test_map()
        self.bundle = create_test_bundle('nonbattle')
        self.hero = self.bundle.tests_get_hero()


    def tearDown(self):
        pass

    def test_charisma(self):
        self.assertTrue(100 < nonbattle.CHARISMA.update_quest_reward(self.hero, 100))

    def test_hackster(self):
        self.assertTrue(100 > nonbattle.HUCKSTER.update_buy_price(self.hero, 100))
        self.assertTrue(100 < nonbattle.HUCKSTER.update_sell_price(self.hero, 100))
