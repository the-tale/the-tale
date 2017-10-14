# coding: utf-8

import collections

from unittest import mock

from the_tale.common.utils import testcase

from the_tale.game.logic import create_test_map
from the_tale.game.logic_storage import LogicStorage

from .. import cards_info
from .. import exceptions


class CardsInfoTests(testcase.TestCase):

    def setUp(self):
        super().setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.info = self.hero.cards

    def test_initialization(self):
        self.assertEqual(self.info._help_count, 0)
        self.assertEqual(self.info._premium_help_count, 0)


    def test_serialization(self):
        self.info.change_help_count(5)
        with mock.patch('the_tale.game.heroes.objects.Hero.is_premium', True):
            self.info.change_help_count(3)

        self.assertEqual(self.info.serialize(), cards_info.CardsInfo.deserialize(self.info.serialize()).serialize())


    def test_change_help_count(self):
        self.assertEqual(self.info.help_count, 0)

        self.info.change_help_count(5)
        self.assertEqual(self.info._help_count, 5)
        self.assertEqual(self.info._premium_help_count, 0)

        with mock.patch('the_tale.game.heroes.objects.Hero.is_premium', True):
            self.info.change_help_count(4)
            self.assertEqual(self.info._help_count, 9)
            self.assertEqual(self.info._premium_help_count, 4)

            self.info.change_help_count(-3)
            self.assertEqual(self.info._help_count, 6)
            self.assertEqual(self.info._premium_help_count, 4)

            self.info.change_help_count(-3)
            self.assertEqual(self.info._help_count, 3)
            self.assertEqual(self.info._premium_help_count, 3)

        self.info.change_help_count(2)
        self.assertEqual(self.info._help_count, 5)
        self.assertEqual(self.info._premium_help_count, 3)

        self.info.change_help_count(-5)
        self.assertEqual(self.info._help_count, 0)
        self.assertEqual(self.info._premium_help_count, 0)


    def test_change_help_count__below_zero(self):
        self.assertRaises(exceptions.HelpCountBelowZero, self.info.change_help_count, -5)


    def check_is_next_card_premium(self, help_count, premium_help_count, result):
        self.hero.cards._help_count = help_count
        self.hero.cards._premium_help_count = premium_help_count
        self.assertEqual(self.hero.cards.is_next_card_premium(), result)


    def test_is_next_card_premium(self):
        self.check_is_next_card_premium(0, 0, False)
        self.check_is_next_card_premium(10, 9, False)
        self.check_is_next_card_premium(10, 10, True)
