# coding: utf-8

import collections

import mock

from the_tale.common.utils import testcase

from the_tale.finances.market import goods_types

from the_tale.game.logic import create_test_map
from the_tale.game.logic_storage import LogicStorage

from the_tale.game.companions import models as companions_models
from the_tale.game.companions import storage as companions_storage
from the_tale.game.companions import logic as companions_logic
from the_tale.game.companions import relations as companions_relations
from the_tale.game.companions.tests import helpers as companions_helpers


from the_tale.game.cards import container
from the_tale.game.cards import relations
from the_tale.game.cards import exceptions
from the_tale.game.cards import objects


class ContainerTests(testcase.TestCase):

    def setUp(self):
        super(ContainerTests, self).setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.container = self.hero.cards


    def test_initialization(self):
        self.assertFalse(self.container.updated)
        self.assertEqual(self.container._cards, {})

    def test_serialization(self):
        self.container.add_card(objects.Card(relations.CARD_TYPE.KEEPERS_GOODS_COMMON))
        self.container.add_card(objects.Card(relations.CARD_TYPE.ADD_GOLD_COMMON, available_for_auction=True))

        self.container.change_help_count(5)
        with mock.patch('the_tale.game.heroes.objects.Hero.is_premium', True):
            self.container.change_help_count(3)

        self.assertEqual(self.container.serialize(), container.CardsContainer.deserialize(self.container.serialize()).serialize())

    def test_add_card(self):
        self.assertFalse(self.container.updated)

        card_1 = objects.Card(relations.CARD_TYPE.KEEPERS_GOODS_COMMON)
        card_2 = objects.Card(relations.CARD_TYPE.ADD_GOLD_COMMON, available_for_auction=True)
        card_3 = objects.Card(relations.CARD_TYPE.KEEPERS_GOODS_LEGENDARY)

        with mock.patch('the_tale.finances.market.goods_types.BaseGoodType.sync_added_item') as sync_added_item:
            self.container.add_card(card_1)
            self.container.add_card(card_2)
            self.container.add_card(card_3)

        self.assertEqual(sync_added_item.call_args_list, [mock.call(self.account.id, card_1),
                                                          mock.call(self.account.id, card_2),
                                                          mock.call(self.account.id, card_3)])

        self.assertTrue(self.container.updated)
        self.assertEqual(self.container._cards, {card_1.uid: card_1,
                                                 card_2.uid: card_2,
                                                 card_3.uid: card_3})


    def test_remove_card(self):
        card_1 = objects.Card(relations.CARD_TYPE.KEEPERS_GOODS_COMMON)
        card_2 = objects.Card(relations.CARD_TYPE.ADD_GOLD_COMMON, available_for_auction=True)

        self.container.add_card(card_1)
        self.container.add_card(card_2)

        self.container.updated = False

        with mock.patch('the_tale.finances.market.goods_types.BaseGoodType.sync_removed_item') as sync_removed_item:
            self.container.remove_card(card_1.uid)

        self.assertEqual(sync_removed_item.call_args_list, [mock.call(self.account.id, card_1)])

        self.assertTrue(self.container.updated)
        self.assertEqual(self.container._cards, {card_2.uid: card_2})


    def test_card_count(self):
        self.assertEqual(len(list(self.container.all_cards())), 0)

        card_1 = objects.Card(relations.CARD_TYPE.KEEPERS_GOODS_COMMON)
        card_2 = objects.Card(relations.CARD_TYPE.KEEPERS_GOODS_COMMON, available_for_auction=True)
        card_3 = objects.Card(relations.CARD_TYPE.ADD_GOLD_COMMON, available_for_auction=True)

        self.container.add_card(card_1)
        self.container.add_card(card_2)
        self.container.add_card(card_3)

        cards_counter = collections.Counter(card.type for card in self.container.all_cards())

        self.assertEqual(cards_counter.get(relations.CARD_TYPE.KEEPERS_GOODS_COMMON), 2)
        self.assertEqual(cards_counter.get(relations.CARD_TYPE.ADD_GOLD_COMMON), 1)
        self.assertEqual(cards_counter.get(relations.CARD_TYPE.ADD_GOLD_RARE), None)


    def test_has_cards(self):
        self.assertFalse(self.container.has_cards)
        self.container.add_card(objects.Card(relations.CARD_TYPE.KEEPERS_GOODS_COMMON))
        self.assertTrue(self.container.has_cards)


    def test_change_help_count(self):
        self.assertEqual(self.container.help_count, 0)

        self.container.change_help_count(5)
        self.assertEqual(self.container._help_count, 5)
        self.assertEqual(self.container._premium_help_count, 0)

        with mock.patch('the_tale.game.heroes.objects.Hero.is_premium', True):
            self.container.change_help_count(4)
            self.assertEqual(self.container._help_count, 9)
            self.assertEqual(self.container._premium_help_count, 4)

            self.container.change_help_count(-3)
            self.assertEqual(self.container._help_count, 6)
            self.assertEqual(self.container._premium_help_count, 4)

            self.container.change_help_count(-3)
            self.assertEqual(self.container._help_count, 3)
            self.assertEqual(self.container._premium_help_count, 3)

        self.container.change_help_count(2)
        self.assertEqual(self.container._help_count, 5)
        self.assertEqual(self.container._premium_help_count, 3)

        self.container.change_help_count(-5)
        self.assertEqual(self.container._help_count, 0)
        self.assertEqual(self.container._premium_help_count, 0)

    def test_change_help_count__below_zero(self):
        self.assertRaises(exceptions.HelpCountBelowZero, self.container.change_help_count, -5)



class GetNewCardTest(testcase.TestCase):

    def setUp(self):
        super(GetNewCardTest, self).setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]


    def test_single_card(self):
        self.assertTrue(self.hero.cards.has_card(self.hero.cards.get_new_card().uid))


    def test_exclude_not_allowrd_effects(self):
        effects = set()

        companions_models.CompanionRecord.objects.all().delete()
        companions_storage.companions.refresh()

        for rarity, rarity_abilities in companions_helpers.RARITIES_ABILITIES.iteritems():
            companions_logic.create_random_companion_record('%s companion' % rarity,
                                                            mode=companions_relations.MODE.AUTOMATIC,
                                                            abilities=rarity_abilities,
                                                            state=companions_relations.STATE.ENABLED)


        @classmethod
        def effect_availability(cls):
            return bool(cls.TYPE.value % 2)

        with mock.patch('the_tale.game.cards.effects.BaseEffect.available', effect_availability):
            with mock.patch('the_tale.game.cards.effects.GetCompanionBase.available', effect_availability):
                for i in xrange(10000):
                    effects.add(self.hero.cards.get_new_card().effect.TYPE)

        for effect_type in relations.CARD_TYPE.records:
            if effect_type.value % 2 == 0:
                self.assertNotIn(effect_type, effects)


    @mock.patch('the_tale.game.heroes.objects.Hero.is_premium', True)
    def test_simple(self):

        rarities = set()

        companions_models.CompanionRecord.objects.all().delete()
        companions_storage.companions.refresh()

        for rarity, rarity_abilities in companions_helpers.RARITIES_ABILITIES.iteritems():
            companions_logic.create_random_companion_record('%s companion' % rarity,
                                                            mode=companions_relations.MODE.AUTOMATIC,
                                                            abilities=rarity_abilities,
                                                            state=companions_relations.STATE.ENABLED)


        for i in xrange(len(relations.CARD_TYPE.records)*10):
            card = self.hero.cards.get_new_card()
            rarities.add(card.type.rarity)

        self.assertTrue(len(relations.CARD_TYPE.records) > len(set(card.type for card in self.hero.cards.all_cards())) / 2)
        self.assertEqual(rarities, set(relations.RARITY.records))

    @mock.patch('the_tale.game.heroes.objects.Hero.is_premium', False)
    def test_not_premium(self):

        for i in xrange(len(relations.CARD_TYPE.records)*10):
            self.hero.cards.get_new_card()

        for card in self.hero.cards.all_cards():
            self.assertFalse(card.type.availability.is_FOR_PREMIUMS)


    @mock.patch('the_tale.game.heroes.objects.Hero.is_premium', False)
    def test_auction_availability_not_specified_not_premium(self):
        self.assertFalse(self.hero.cards.get_new_card().available_for_auction)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_premium', True)
    def test_auction_availability_not_specified_premium(self):
        self.assertTrue(self.hero.cards.get_new_card().available_for_auction)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_premium', False)
    def test_auction_availability_false_not_premium(self):
        self.assertFalse(self.hero.cards.get_new_card(available_for_auction=False).available_for_auction)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_premium', True)
    def test_auction_availability_false_premium(self):
        self.assertFalse(self.hero.cards.get_new_card(available_for_auction=False).available_for_auction)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_premium', False)
    def test_auction_availability_true_not_premium(self):
        self.assertTrue(self.hero.cards.get_new_card(available_for_auction=True).available_for_auction)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_premium', True)
    def test_auction_availability_true_premium(self):
        self.assertTrue(self.hero.cards.get_new_card(available_for_auction=True).available_for_auction)


    @mock.patch('the_tale.game.heroes.objects.Hero.is_premium', True)
    def test_priority(self):
        for i in xrange(len(relations.CARD_TYPE.records)*100):
            self.hero.cards.get_new_card()

        rarities = collections.Counter(card.type.rarity for card in self.hero.cards.all_cards())

        last_rarity_count = 999999999999

        for rarity in relations.RARITY.records:
            self.assertTrue(last_rarity_count >= rarities[rarity])
            last_rarity_count = rarities[rarity]

    @mock.patch('the_tale.game.heroes.objects.Hero.is_premium', True)
    def test_rarity(self):
        for rarity in relations.RARITY.records:
            for i in xrange(100):
                card = self.hero.cards.get_new_card(rarity=rarity)
                self.assertEqual(card.type.rarity, rarity)


    @mock.patch('the_tale.game.heroes.objects.Hero.is_premium', True)
    def test_exclude(self):
        cards = []

        companions_models.CompanionRecord.objects.all().delete()
        companions_storage.companions.refresh()

        for rarity, rarity_abilities in companions_helpers.RARITIES_ABILITIES.iteritems():
            companions_logic.create_random_companion_record('%s companion' % rarity,
                                                            mode=companions_relations.MODE.AUTOMATIC,
                                                            abilities=rarity_abilities,
                                                            state=companions_relations.STATE.ENABLED)

        for i in xrange(len(relations.CARD_TYPE.records)):
            card = self.hero.cards.get_new_card(exclude=cards)
            cards.append(card)

        self.assertEqual(self.hero.cards.get_new_card(exclude=cards), None)

        self.assertEqual(set(card.type for card in cards), set(relations.CARD_TYPE.records))


    @mock.patch('the_tale.game.heroes.objects.Hero.is_premium', True)
    def test_exclude__different_data(self):
        cards = []

        companions_models.CompanionRecord.objects.all().delete()
        companions_storage.companions.refresh()

        for rarity, rarity_abilities in companions_helpers.RARITIES_ABILITIES.iteritems():
            companions_logic.create_random_companion_record('%s companion' % rarity,
                                                            mode=companions_relations.MODE.AUTOMATIC,
                                                            abilities=rarity_abilities,
                                                            state=companions_relations.STATE.ENABLED)


        for i in xrange(len(relations.CARD_TYPE.records)):
            card = self.hero.cards.get_new_card(exclude=cards)
            cards.append(card)

        self.assertEqual(self.hero.cards.get_new_card(exclude=cards), None)

        cards[0].data = {'fake-data': True}
        self.assertEqual(cards[0].type, self.hero.cards.get_new_card(exclude=cards).type)

        self.assertEqual(set(card.type for card in cards), set(relations.CARD_TYPE.records))


class CanCombineCardsTests(testcase.TestCase):

    def setUp(self):
        super(CanCombineCardsTests, self).setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.card__add_power_common_1 = objects.Card(type=relations.CARD_TYPE.ADD_POWER_COMMON)
        self.card__add_power_common_2 = objects.Card(type=relations.CARD_TYPE.ADD_POWER_COMMON)
        self.card__add_power_common_3 = objects.Card(type=relations.CARD_TYPE.ADD_POWER_COMMON)
        self.card__add_power_common_4 = objects.Card(type=relations.CARD_TYPE.ADD_POWER_COMMON)

        self.card__add_bonus_energy_common_1 = objects.Card(type=relations.CARD_TYPE.ADD_BONUS_ENERGY_COMMON)

        self.card__add_bonus_energy_legendary_1 = objects.Card(type=relations.CARD_TYPE.ADD_BONUS_ENERGY_LEGENDARY)
        self.card__add_bonus_energy_legendary_2 = objects.Card(type=relations.CARD_TYPE.ADD_BONUS_ENERGY_LEGENDARY)
        self.card__add_bonus_energy_legendary_3 = objects.Card(type=relations.CARD_TYPE.ADD_BONUS_ENERGY_LEGENDARY)

        self.card__add_gold_common_1 = objects.Card(type=relations.CARD_TYPE.ADD_GOLD_COMMON)

        self.hero.cards.add_card(self.card__add_power_common_1)
        self.hero.cards.add_card(self.card__add_power_common_2)
        self.hero.cards.add_card(self.card__add_power_common_3)
        self.hero.cards.add_card(self.card__add_power_common_4)

        self.hero.cards.add_card(self.card__add_bonus_energy_common_1)

        self.hero.cards.add_card(self.card__add_bonus_energy_legendary_1)
        self.hero.cards.add_card(self.card__add_bonus_energy_legendary_2)
        self.hero.cards.add_card(self.card__add_bonus_energy_legendary_3)

        self.hero.cards.add_card(self.card__add_gold_common_1)


    def test_not_enough_cards(self):
        self.assertTrue(self.hero.cards.can_combine_cards([]).is_NOT_ENOUGH_CARDS)
        self.assertTrue(self.hero.cards.can_combine_cards([]).is_NOT_ENOUGH_CARDS)
        self.assertFalse(self.hero.cards.can_combine_cards([self.card__add_power_common_1.uid,
                                                            self.card__add_power_common_2.uid]).is_NOT_ENOUGH_CARDS)

    def test_to_many_cards(self):
        self.assertFalse(self.hero.cards.can_combine_cards([self.card__add_power_common_1.uid,
                                                            self.card__add_power_common_2.uid]).is_TO_MANY_CARDS)
        self.assertFalse(self.hero.cards.can_combine_cards([self.card__add_power_common_1.uid,
                                                            self.card__add_power_common_2.uid,
                                                            self.card__add_power_common_3.uid]).is_TO_MANY_CARDS)
        self.assertTrue(self.hero.cards.can_combine_cards([self.card__add_power_common_1.uid,
                                                           self.card__add_power_common_2.uid,
                                                           self.card__add_power_common_3.uid,
                                                           self.card__add_power_common_4.uid]).is_TO_MANY_CARDS)

    def test_equal_rarity_required(self):
        self.assertNotEqual(self.card__add_power_common_1.type.rarity, self.card__add_bonus_energy_legendary_1.type.rarity)
        self.assertTrue(self.hero.cards.can_combine_cards([self.card__add_power_common_1.uid,
                                                           self.card__add_bonus_energy_legendary_1.uid]).is_EQUAL_RARITY_REQUIRED)

        self.assertEqual(self.card__add_power_common_1.type.rarity, self.card__add_bonus_energy_common_1.type.rarity)
        self.assertFalse(self.hero.cards.can_combine_cards([self.card__add_power_common_1.uid,
                                                            self.card__add_bonus_energy_common_1.uid]).is_EQUAL_RARITY_REQUIRED)

    def test_legendary_x3(self):
        self.assertTrue(self.card__add_bonus_energy_legendary_1.type.rarity.is_LEGENDARY)
        self.assertTrue(self.hero.cards.can_combine_cards([self.card__add_bonus_energy_legendary_1.uid,
                                                           self.card__add_bonus_energy_legendary_2.uid,
                                                           self.card__add_bonus_energy_legendary_3.uid]).is_LEGENDARY_X3_DISALLOWED)
        self.assertFalse(self.hero.cards.can_combine_cards([self.card__add_bonus_energy_legendary_1.uid,
                                                           self.card__add_bonus_energy_legendary_2.uid]).is_LEGENDARY_X3_DISALLOWED)


    def test_no_cards(self):
        self.assertTrue(self.hero.cards.can_combine_cards([666, 667]).is_HAS_NO_CARDS)
        self.assertTrue(self.hero.cards.can_combine_cards([self.card__add_power_common_1, 667]).is_HAS_NO_CARDS)
        self.assertTrue(self.hero.cards.can_combine_cards([666, self.card__add_power_common_1]).is_HAS_NO_CARDS)


    def test_allowed(self):
        self.assertTrue(self.hero.cards.can_combine_cards([self.card__add_power_common_1.uid,
                                                           self.card__add_power_common_2.uid,]).is_ALLOWED)

        self.assertTrue(self.hero.cards.can_combine_cards([self.card__add_power_common_1.uid,
                                                           self.card__add_power_common_2.uid,
                                                           self.card__add_bonus_energy_common_1.uid]).is_ALLOWED)

        self.assertTrue(self.hero.cards.can_combine_cards([self.card__add_power_common_1.uid,
                                                           self.card__add_power_common_2.uid,
                                                           self.card__add_power_common_3.uid]).is_ALLOWED)

        self.assertTrue(self.hero.cards.can_combine_cards([self.card__add_power_common_1.uid,
                                                           self.card__add_bonus_energy_common_1.uid,
                                                           self.card__add_gold_common_1.uid]).is_ALLOWED)




class CombineCardsTests(testcase.TestCase):

    def setUp(self):
        super(CombineCardsTests, self).setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.card__add_power_common_1 = objects.Card(type=relations.CARD_TYPE.ADD_POWER_COMMON)
        self.card__add_power_common_2 = objects.Card(type=relations.CARD_TYPE.ADD_POWER_COMMON)
        self.card__add_power_common_3 = objects.Card(type=relations.CARD_TYPE.ADD_POWER_COMMON)
        self.card__add_power_common_4 = objects.Card(type=relations.CARD_TYPE.ADD_POWER_COMMON)

        self.card__add_bonus_energy_common_1 = objects.Card(type=relations.CARD_TYPE.ADD_BONUS_ENERGY_COMMON)

        self.card__add_bonus_energy_legendary_1 = objects.Card(type=relations.CARD_TYPE.ADD_BONUS_ENERGY_LEGENDARY)
        self.card__add_bonus_energy_legendary_2 = objects.Card(type=relations.CARD_TYPE.ADD_BONUS_ENERGY_LEGENDARY)
        self.card__add_bonus_energy_legendary_3 = objects.Card(type=relations.CARD_TYPE.ADD_BONUS_ENERGY_LEGENDARY)

        self.card__add_gold_common_1 = objects.Card(type=relations.CARD_TYPE.ADD_GOLD_COMMON)

        self.hero.cards.add_card(self.card__add_power_common_1)
        self.hero.cards.add_card(self.card__add_power_common_2)
        self.hero.cards.add_card(self.card__add_power_common_3)
        self.hero.cards.add_card(self.card__add_power_common_4)

        self.hero.cards.add_card(self.card__add_bonus_energy_common_1)

        self.hero.cards.add_card(self.card__add_bonus_energy_legendary_1)
        self.hero.cards.add_card(self.card__add_bonus_energy_legendary_2)
        self.hero.cards.add_card(self.card__add_bonus_energy_legendary_3)

        self.hero.cards.add_card(self.card__add_gold_common_1)


    def test_2_cards(self):
        with self.check_delta(self.hero.cards.cards_count, -1):
            card = self.hero.cards.combine_cards([self.card__add_power_common_1.uid, self.card__add_bonus_energy_common_1.uid])

        self.assertFalse(self.hero.cards.has_card(self.card__add_power_common_1.uid))
        self.assertFalse(self.hero.cards.has_card(self.card__add_bonus_energy_common_1.uid))
        self.assertTrue(self.hero.cards.has_card(card.uid))

        self.assertNotIn(card.type, (self.card__add_bonus_energy_common_1.type,
                                     self.card__add_bonus_energy_common_1.type))
        self.assertTrue(card.type.rarity.is_COMMON)


    def test_3_cards(self):
        with self.check_delta(self.hero.cards.cards_count, -2):
            card = self.hero.cards.combine_cards([self.card__add_power_common_1.uid,
                                                  self.card__add_bonus_energy_common_1.uid,
                                                  self.card__add_gold_common_1.uid])

        self.assertFalse(self.hero.cards.has_card(self.card__add_power_common_1.uid))
        self.assertFalse(self.hero.cards.has_card(self.card__add_bonus_energy_common_1.uid))
        self.assertFalse(self.hero.cards.has_card(self.card__add_gold_common_1.uid))

        self.assertNotIn(card.type, (self.card__add_bonus_energy_common_1.type,
                                     self.card__add_bonus_energy_common_1.type,
                                     self.card__add_gold_common_1.type))

        self.assertTrue(self.hero.cards.has_card(card.uid))
        self.assertTrue(card.type.rarity.is_UNCOMMON)


    @mock.patch('the_tale.game.heroes.objects.Hero.is_premium', True)
    def test_auction_availability__not_available__hero_premium(self):
        self.card__add_power_common_1.available_for_auction = True
        self.card__add_bonus_energy_common_1.available_for_auction = False
        self.card__add_gold_common_1.available_for_auction = True

        card = self.hero.cards.combine_cards([self.card__add_power_common_1.uid,
                                              self.card__add_bonus_energy_common_1.uid,
                                              self.card__add_gold_common_1.uid])

        self.assertFalse(card.available_for_auction)


    @mock.patch('the_tale.game.heroes.objects.Hero.is_premium', True)
    def test_auction_availability__available__hero_premium(self):
        self.card__add_power_common_1.available_for_auction = True
        self.card__add_bonus_energy_common_1.available_for_auction = True
        self.card__add_gold_common_1.available_for_auction = True

        card = self.hero.cards.combine_cards([self.card__add_power_common_1.uid,
                                              self.card__add_bonus_energy_common_1.uid,
                                              self.card__add_gold_common_1.uid])

        self.assertTrue(card.available_for_auction)


    @mock.patch('the_tale.game.heroes.objects.Hero.is_premium', False)
    def test_auction_availability__not_available__hero_not_premium(self):
        self.card__add_power_common_1.available_for_auction = True
        self.card__add_bonus_energy_common_1.available_for_auction = False
        self.card__add_gold_common_1.available_for_auction = True

        card = self.hero.cards.combine_cards([self.card__add_power_common_1.uid,
                                              self.card__add_bonus_energy_common_1.uid,
                                              self.card__add_gold_common_1.uid])

        self.assertFalse(card.available_for_auction)


    @mock.patch('the_tale.game.heroes.objects.Hero.is_premium', False)
    def test_auction_availability__available__hero_not_premium(self):
        self.card__add_power_common_1.available_for_auction = True
        self.card__add_bonus_energy_common_1.available_for_auction = True
        self.card__add_gold_common_1.available_for_auction = True

        card = self.hero.cards.combine_cards([self.card__add_power_common_1.uid,
                                              self.card__add_bonus_energy_common_1.uid,
                                              self.card__add_gold_common_1.uid])

        self.assertTrue(card.available_for_auction)
