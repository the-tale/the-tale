# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.game.logic import create_test_map
from the_tale.game.logic_storage import LogicStorage

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
        self.container.add_card(relations.CARD_TYPE.KEEPERS_GOODS_COMMON, 666)
        self.assertEqual(self.container.serialize(), container.CardsContainer.deserialize('hero', self.container.serialize()).serialize())


    def test_add_card(self):
        self.container.add_card(relations.CARD_TYPE.KEEPERS_GOODS_COMMON, 6)

        self.assertTrue(self.container.updated)
        self.assertEqual(self.container._cards, {relations.CARD_TYPE.KEEPERS_GOODS_COMMON: 6})


    def test_add_card__increment(self):
        self.container.add_card(relations.CARD_TYPE.KEEPERS_GOODS_COMMON, 1)
        self.container.add_card(relations.CARD_TYPE.KEEPERS_GOODS_COMMON, 6)

        self.assertTrue(self.container.updated)
        self.assertEqual(self.container._cards, {relations.CARD_TYPE.KEEPERS_GOODS_COMMON: 7})


    def test_remove_card(self):
        self.container.add_card(relations.CARD_TYPE.KEEPERS_GOODS_COMMON, 6)
        self.container.updated = False

        self.container.remove_card(relations.CARD_TYPE.KEEPERS_GOODS_COMMON, 4)

        self.assertTrue(self.container.updated)
        self.assertEqual(self.container._cards, {relations.CARD_TYPE.KEEPERS_GOODS_COMMON: 2})


    def test_remove_card__remove(self):
        self.container.add_card(relations.CARD_TYPE.KEEPERS_GOODS_COMMON, 6)
        self.container.updated = False

        self.container.remove_card(relations.CARD_TYPE.KEEPERS_GOODS_COMMON, 6)

        self.assertTrue(self.container.updated)
        self.assertEqual(self.container._cards, {})


    def test_remove_card__not_enough(self):
        self.container.add_card(relations.CARD_TYPE.KEEPERS_GOODS_COMMON, 6)
        self.assertRaises(exceptions.RemoveUnexistedCardError, self.container.remove_card, relations.CARD_TYPE.KEEPERS_GOODS_COMMON, 7)


    def test_card_count(self):
        self.assertEqual(self.container.card_count(relations.CARD_TYPE.KEEPERS_GOODS_COMMON), 0)
        self.container.add_card(relations.CARD_TYPE.KEEPERS_GOODS_COMMON, 6)
        self.assertEqual(self.container.card_count(relations.CARD_TYPE.KEEPERS_GOODS_COMMON), 6)


    def test_has_cards(self):
        self.assertFalse(self.container.has_cards)
        self.container.add_card(relations.CARD_TYPE.KEEPERS_GOODS_COMMON, 6)
        self.assertTrue(self.container.has_cards)





class GetNewCardTest(testcase.TestCase):

    def setUp(self):
        super(GetNewCardTest, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

    def test_singe_card(self):
        self.assertTrue(self.hero.cards.has_card(self.hero.cards.get_new_card()))


    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.is_premium', True)
    def test_simple(self):

        rarities = set()

        for i in xrange(len(relations.CARD_TYPE.records)*1000):
            card = self.hero.cards.get_new_card()
            rarities.add(card.rarity)

        self.assertEqual(len(relations.CARD_TYPE.records), len(self.hero.cards.cards))
        self.assertEqual(rarities, set(relations.RARITY.records))

    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.is_premium', False)
    def test_not_premium(self):

        for i in xrange(len(relations.CARD_TYPE.records)*10):
            self.hero.cards.get_new_card()

        for card in relations.CARD_TYPE.records:
            if self.hero.cards.has_card(card):
                self.assertFalse(card.availability.is_FOR_PREMIUMS)

    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.is_premium', True)
    def test_priority(self):
        for i in xrange(len(relations.CARD_TYPE.records)*1000):
            self.hero.cards.get_new_card()

        last_rarity_value = -1

        for card, count in sorted(self.hero.cards.cards, key=lambda x: -x[1]):
            self.assertTrue(last_rarity_value <= card.rarity.value)
            last_rarity_value = card.rarity.value

    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.is_premium', True)
    def test_rarity(self):
        for rarity in relations.RARITY.records:
            for i in xrange(100):
                card = self.hero.cards.get_new_card(rarity=rarity)
                self.assertEqual(card.rarity, rarity)


    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.is_premium', True)
    def test_exclude(self):
        cards = set()

        for i in xrange(len(relations.CARD_TYPE.records)):
            cards.add(self.hero.cards.get_new_card(exclude=cards))

        self.assertEqual(cards, set(relations.CARD_TYPE.records))


class CanCombineCardsTests(testcase.TestCase):

    def setUp(self):
        super(CanCombineCardsTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]


    def test_not_enough_cards(self):
        self.assertTrue(self.hero.cards.can_combine_cards([]).is_NOT_ENOUGH_CARDS)
        self.assertTrue(self.hero.cards.can_combine_cards([relations.CARD_TYPE.ADD_POWER_COMMON]).is_NOT_ENOUGH_CARDS)
        self.assertFalse(self.hero.cards.can_combine_cards([relations.CARD_TYPE.ADD_POWER_COMMON]*2).is_NOT_ENOUGH_CARDS)

    def test_to_many_cards(self):
        self.assertFalse(self.hero.cards.can_combine_cards([relations.CARD_TYPE.ADD_POWER_COMMON]*2).is_TO_MANY_CARDS)
        self.assertFalse(self.hero.cards.can_combine_cards([relations.CARD_TYPE.ADD_POWER_COMMON]*3).is_TO_MANY_CARDS)
        self.assertTrue(self.hero.cards.can_combine_cards([relations.CARD_TYPE.ADD_POWER_COMMON]*4).is_TO_MANY_CARDS)

    def test_equal_rarity_required(self):
        self.assertNotEqual(relations.CARD_TYPE.ADD_POWER_COMMON.rarity, relations.CARD_TYPE.ADD_BONUS_ENERGY_LEGENDARY.rarity)
        self.assertTrue(self.hero.cards.can_combine_cards([relations.CARD_TYPE.ADD_POWER_COMMON, relations.CARD_TYPE.ADD_BONUS_ENERGY_LEGENDARY]).is_EQUAL_RARITY_REQUIRED)

        self.assertEqual(relations.CARD_TYPE.ADD_POWER_COMMON.rarity, relations.CARD_TYPE.ADD_BONUS_ENERGY_COMMON.rarity)
        self.assertFalse(self.hero.cards.can_combine_cards([relations.CARD_TYPE.ADD_POWER_COMMON, relations.CARD_TYPE.ADD_BONUS_ENERGY_COMMON]).is_EQUAL_RARITY_REQUIRED)

    def test_legendary_x3(self):
        self.assertTrue(relations.CARD_TYPE.ADD_BONUS_ENERGY_LEGENDARY.rarity.is_LEGENDARY)
        self.assertTrue(self.hero.cards.can_combine_cards([relations.CARD_TYPE.ADD_BONUS_ENERGY_LEGENDARY]*3).is_LEGENDARY_X3_DISALLOWED)
        self.assertFalse(self.hero.cards.can_combine_cards([relations.CARD_TYPE.ADD_BONUS_ENERGY_LEGENDARY]*2).is_LEGENDARY_X3_DISALLOWED)

    def test_no_cards(self):
        self.assertTrue(self.hero.cards.can_combine_cards([relations.CARD_TYPE.ADD_POWER_COMMON, relations.CARD_TYPE.ADD_BONUS_ENERGY_COMMON]).is_HAS_NO_CARDS)

        self.hero.cards.add_card(relations.CARD_TYPE.ADD_POWER_COMMON, 1)

        self.assertTrue(self.hero.cards.can_combine_cards([relations.CARD_TYPE.ADD_POWER_COMMON, relations.CARD_TYPE.ADD_BONUS_ENERGY_COMMON]).is_HAS_NO_CARDS)

        self.hero.cards.add_card(relations.CARD_TYPE.ADD_BONUS_ENERGY_COMMON, 1)

        self.assertFalse(self.hero.cards.can_combine_cards([relations.CARD_TYPE.ADD_POWER_COMMON, relations.CARD_TYPE.ADD_BONUS_ENERGY_COMMON]).is_HAS_NO_CARDS)


    def test_no_cards__stacked(self):
        self.assertTrue(self.hero.cards.can_combine_cards([relations.CARD_TYPE.ADD_POWER_COMMON]*2).is_HAS_NO_CARDS)

        self.hero.cards.add_card(relations.CARD_TYPE.ADD_POWER_COMMON, 1)

        self.assertTrue(self.hero.cards.can_combine_cards([relations.CARD_TYPE.ADD_POWER_COMMON]*2).is_HAS_NO_CARDS)

        self.hero.cards.add_card(relations.CARD_TYPE.ADD_POWER_COMMON, 1)

        self.assertFalse(self.hero.cards.can_combine_cards([relations.CARD_TYPE.ADD_POWER_COMMON]*2).is_HAS_NO_CARDS)


    def test_allowed(self):
        self.hero.cards.add_card(relations.CARD_TYPE.ADD_POWER_COMMON, 3)
        self.hero.cards.add_card(relations.CARD_TYPE.ADD_BONUS_ENERGY_COMMON, 3)
        self.hero.cards.add_card(relations.CARD_TYPE.ADD_GOLD_COMMON, 3)

        self.assertTrue(self.hero.cards.can_combine_cards([relations.CARD_TYPE.ADD_POWER_COMMON]*2).is_ALLOWED)
        self.assertTrue(self.hero.cards.can_combine_cards([relations.CARD_TYPE.ADD_POWER_COMMON]*2+[relations.CARD_TYPE.ADD_BONUS_ENERGY_COMMON]).is_ALLOWED)
        self.assertTrue(self.hero.cards.can_combine_cards([relations.CARD_TYPE.ADD_POWER_COMMON]*3).is_ALLOWED)
        self.assertTrue(self.hero.cards.can_combine_cards([relations.CARD_TYPE.ADD_POWER_COMMON, relations.CARD_TYPE.ADD_BONUS_ENERGY_COMMON, relations.CARD_TYPE.ADD_GOLD_COMMON]).is_ALLOWED)
