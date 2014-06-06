# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.game.cards import container
from the_tale.game.cards import relations
from the_tale.game.cards import exceptions


class ContainerTests(testcase.TestCase):

    def setUp(self):
        super(ContainerTests, self).setUp()
        self.container = container.CardsContainer()


    def test_initialization(self):
        self.assertFalse(self.container.updated)
        self.assertEqual(self.container._cards, {})

    def test_serialization(self):
        self.container.add_card(relations.CARD_TYPE.KEEPERS_GOODS, 666)
        self.assertEqual(self.container.serialize(), container.CardsContainer.deserialize('hero', self.container.serialize()).serialize())


    def test_add_card(self):
        self.container.add_card(relations.CARD_TYPE.KEEPERS_GOODS, 6)

        self.assertTrue(self.container.updated)
        self.assertEqual(self.container._cards, {relations.CARD_TYPE.KEEPERS_GOODS: 6})


    def test_add_card__increment(self):
        self.container.add_card(relations.CARD_TYPE.KEEPERS_GOODS, 1)
        self.container.add_card(relations.CARD_TYPE.KEEPERS_GOODS, 6)

        self.assertTrue(self.container.updated)
        self.assertEqual(self.container._cards, {relations.CARD_TYPE.KEEPERS_GOODS: 7})


    def test_remove_card(self):
        self.container.add_card(relations.CARD_TYPE.KEEPERS_GOODS, 6)
        self.container.updated = False

        self.container.remove_card(relations.CARD_TYPE.KEEPERS_GOODS, 4)

        self.assertTrue(self.container.updated)
        self.assertEqual(self.container._cards, {relations.CARD_TYPE.KEEPERS_GOODS: 2})


    def test_remove_card__remove(self):
        self.container.add_card(relations.CARD_TYPE.KEEPERS_GOODS, 6)
        self.container.updated = False

        self.container.remove_card(relations.CARD_TYPE.KEEPERS_GOODS, 6)

        self.assertTrue(self.container.updated)
        self.assertEqual(self.container._cards, {})


    def test_remove_card__not_enough(self):
        self.container.add_card(relations.CARD_TYPE.KEEPERS_GOODS, 6)
        self.assertRaises(exceptions.RemoveUnexistedCardError, self.container.remove_card, relations.CARD_TYPE.KEEPERS_GOODS, 7)


    def test_card_count(self):
        self.assertEqual(self.container.card_count(relations.CARD_TYPE.KEEPERS_GOODS), 0)
        self.container.add_card(relations.CARD_TYPE.KEEPERS_GOODS, 6)
        self.assertEqual(self.container.card_count(relations.CARD_TYPE.KEEPERS_GOODS), 6)


    def test_has_cards(self):
        self.assertFalse(self.container.has_cards)
        self.container.add_card(relations.CARD_TYPE.KEEPERS_GOODS, 6)
        self.assertTrue(self.container.has_cards)
