
import uuid
import collections

from unittest import mock

from the_tale.common.utils import testcase

from the_tale.game.logic import create_test_map
from the_tale.game import relations as game_relations

from the_tale.game.companions import models as companions_models
from the_tale.game.companions import storage as companions_storage
from the_tale.game.companions import logic as companions_logic
from the_tale.game.companions import relations as companions_relations
from the_tale.game.companions.tests import helpers as companions_helpers

from the_tale.game.heroes import relations as heroes_relations

from .. import logic
from .. import cards
from .. import effects
from .. import relations


class CreateCardTest(testcase.TestCase):

    def setUp(self):
        super().setUp()
        create_test_map()

    def test_single_card(self):
        card = logic.create_card(allow_premium_cards=False)
        self.assertTrue(card.uid)

    def test_simple(self):

        created_cards = set()
        rarities = set()

        companions_models.CompanionRecord.objects.all().delete()
        companions_storage.companions.refresh()

        for rarity, rarity_abilities in companions_helpers.RARITIES_ABILITIES.items():
            companions_logic.create_random_companion_record('%s companion' % rarity,
                                                            mode=companions_relations.MODE.AUTOMATIC,
                                                            abilities=rarity_abilities,
                                                            state=companions_relations.STATE.ENABLED)

        for i in range(len(cards.CARD.records)*10):
            card = logic.create_card(allow_premium_cards=True)
            created_cards.add(card.type)
            rarities.add(card.type.rarity)

        self.assertTrue(len(cards.CARD.records) > len(created_cards) / 2)
        self.assertEqual(rarities, set(relations.RARITY.records))

    def test_not_premium(self):
        for i in range(len(cards.CARD.records)*10):
            card = logic.create_card(allow_premium_cards=False)
            self.assertFalse(card.type.availability.is_FOR_PREMIUMS)

    def test_auction_availability_not_specified_not_premium(self):
        self.assertFalse(logic.create_card(allow_premium_cards=True, available_for_auction=False).available_for_auction)
        self.assertTrue(logic.create_card(allow_premium_cards=True, available_for_auction=True).available_for_auction)

    def test_priority(self):
        rarities = collections.Counter(logic.create_card(allow_premium_cards=True).type.rarity
                                       for i in range(len(cards.CARD.records)*100))

        last_rarity_count = 999999999999

        for rarity in relations.RARITY.records:
            self.assertTrue(last_rarity_count >= rarities[rarity])
            last_rarity_count = rarities[rarity]

    def test_rarity(self):
        for rarity in relations.RARITY.records:
            for i in range(100):
                card = logic.create_card(allow_premium_cards=True, rarity=rarity)
                self.assertEqual(card.type.rarity, rarity)

    @mock.patch('the_tale.game.cards.effects.ChangePreference.allowed_preferences', lambda self: [heroes_relations.PREFERENCE_TYPE.records[0]])
    @mock.patch('the_tale.game.cards.effects.ChangeItemOfExpenditure.allowed_items', lambda self: [heroes_relations.ITEMS_OF_EXPENDITURE.records[0]])
    @mock.patch('the_tale.game.cards.effects.ChangeHabit.allowed_habits', lambda self: [game_relations.HABIT_TYPE.records[0]])
    @mock.patch('the_tale.game.cards.effects.ChangeHabit.allowed_directions', lambda self: [1])
    @mock.patch('the_tale.game.cards.effects.AddPersonPower.allowed_directions', lambda self: [1])
    @mock.patch('the_tale.game.cards.effects.AddPlacePower.allowed_directions', lambda self: [1])
    @mock.patch('the_tale.game.cards.effects.ChangeHistory.allowed_history', lambda self: [effects.ChangeHistory.HISTORY_TYPE.records[0]])
    def test_exclude(self):
        created_cards = []

        companions_models.CompanionRecord.objects.all().delete()
        companions_storage.companions.refresh()

        for rarity, rarity_abilities in companions_helpers.RARITIES_ABILITIES.items():
            companions_logic.create_random_companion_record('%s companion' % rarity,
                                                            mode=companions_relations.MODE.AUTOMATIC,
                                                            abilities=rarity_abilities,
                                                            state=companions_relations.STATE.ENABLED)

        for i in range(len([card_type for card_type in cards.CARD.records])):
            card = logic.create_card(allow_premium_cards=True, exclude=created_cards)
            created_cards.append(card)

        self.assertEqual(logic.create_card(allow_premium_cards=True, exclude=created_cards), None)

        self.assertEqual(set(card.type for card in created_cards), set(card_type for card_type in cards.CARD.records))

    @mock.patch('the_tale.game.cards.effects.ChangePreference.allowed_preferences', lambda self: [heroes_relations.PREFERENCE_TYPE.records[0]])
    @mock.patch('the_tale.game.cards.effects.ChangeItemOfExpenditure.allowed_items', lambda self: [heroes_relations.ITEMS_OF_EXPENDITURE.records[0]])
    @mock.patch('the_tale.game.cards.effects.ChangeHabit.allowed_habits', lambda self: [game_relations.HABIT_TYPE.records[0]])
    @mock.patch('the_tale.game.cards.effects.ChangeHabit.allowed_directions', lambda self: [1])
    @mock.patch('the_tale.game.cards.effects.AddPersonPower.allowed_directions', lambda self: [1])
    @mock.patch('the_tale.game.cards.effects.AddPlacePower.allowed_directions', lambda self: [1])
    @mock.patch('the_tale.game.cards.effects.ChangeHistory.allowed_history', lambda self: [effects.ChangeHistory.HISTORY_TYPE.records[0]])
    def test_exclude__different_data(self):
        created_cards = []

        companions_models.CompanionRecord.objects.all().delete()
        companions_storage.companions.refresh()

        for rarity, rarity_abilities in companions_helpers.RARITIES_ABILITIES.items():
            companions_logic.create_random_companion_record('%s companion' % rarity,
                                                            mode=companions_relations.MODE.AUTOMATIC,
                                                            abilities=rarity_abilities,
                                                            state=companions_relations.STATE.ENABLED)

        for i in range(len([card_type for card_type in cards.CARD.records])):
            card = logic.create_card(allow_premium_cards=True, exclude=created_cards)
            created_cards.append(card)

        self.assertEqual(logic.create_card(allow_premium_cards=True, exclude=created_cards), None)

        created_cards[0].data = {'fake-data': True}
        self.assertEqual(created_cards[0].type, logic.create_card(allow_premium_cards=True, exclude=created_cards).type)

        self.assertEqual(set(card.type for card in created_cards), set(card_type for card_type in cards.CARD.records))


class GetCombinedCardTests(testcase.TestCase):

    def setUp(self):
        super().setUp()
        create_test_map()

    def create_card(self, type, available_for_auction=True, uid=None):
        return type.effect.create_card(type=type,
                                       uid=uid,
                                       available_for_auction=available_for_auction)

    def test_no_cards(self):
        card, result = logic.get_combined_card(allow_premium_cards=True,
                                               combined_cards=())
        self.assertEqual(card, None)
        self.assertTrue(result.is_NO_CARDS)

    def test_equal_rarity_required(self):
        card, result = logic.get_combined_card(allow_premium_cards=True,
                                               combined_cards=(self.create_card(cards.CARD.ADD_POWER_COMMON),
                                                               self.create_card(cards.CARD.ADD_POWER_UNCOMMON)))
        self.assertEqual(card, None)
        self.assertTrue(result.is_EQUAL_RARITY_REQUIRED)

    def test_duplicate_ids(self):
        uid = uuid.uuid4()
        card, result = logic.get_combined_card(allow_premium_cards=True,
                                               combined_cards=(self.create_card(cards.CARD.ADD_POWER_COMMON, uid=uid),
                                                               self.create_card(cards.CARD.ADD_POWER_UNCOMMON, uid=uid)))
        self.assertEqual(card, None)
        self.assertTrue(result.is_EQUAL_RARITY_REQUIRED)

    def test_combine_1_common(self):
        card, result = logic.get_combined_card(allow_premium_cards=True,
                                               combined_cards=(self.create_card(cards.CARD.ADD_POWER_COMMON),))
        self.assertEqual(card, None)
        self.assertTrue(result.is_COMBINE_1_COMMON)

    def test_combine_1(self):
        card, result = logic.get_combined_card(allow_premium_cards=True,
                                               combined_cards=(self.create_card(cards.CARD.ADD_POWER_UNCOMMON)
                                                               ,))
        self.assertNotEqual(card, None)
        self.assertTrue(card.type.rarity.is_COMMON)
        self.assertTrue(result.is_SUCCESS)

    def test_combine_2_reactor(self):
        combined_card_1 = self.create_card(cards.CARD.CHANGE_HABIT_EPIC)
        combined_card_2 = self.create_card(cards.CARD.CHANGE_HABIT_EPIC)

        card, result = logic.get_combined_card(allow_premium_cards=True,
                                               combined_cards=(combined_card_1, combined_card_2))
        self.assertNotEqual(card, None)
        self.assertTrue(result.is_SUCCESS)

        self.assertEqual(card.type, cards.CARD.CHANGE_HABIT_EPIC)
        self.assertNotEqual(combined_card_1.data, card.data)
        self.assertNotEqual(combined_card_2.data, card.data)

    def test_combine_2_random(self):
        card, result = logic.get_combined_card(allow_premium_cards=True,
                                               combined_cards=(self.create_card(cards.CARD.CHANGE_HABIT_EPIC),
                                                               self.create_card(cards.CARD.ADD_EXPERIENCE_EPIC)))
        self.assertNotEqual(card, None)
        self.assertTrue(result.is_SUCCESS)

    def test_get_combined_card_3_reactor(self):
        combined_card_1 = self.create_card(cards.CARD.CHANGE_HABIT_EPIC)
        combined_card_2 = self.create_card(cards.CARD.CHANGE_HABIT_EPIC)
        combined_card_3 = self.create_card(cards.CARD.CHANGE_HABIT_EPIC)

        combined_card_2.data = combined_card_1.data
        combined_card_3.data = combined_card_1.data

        card, result = logic.get_combined_card(allow_premium_cards=True,
                                               combined_cards=(combined_card_1, combined_card_2, combined_card_3))
        self.assertNotEqual(card, None)
        self.assertTrue(result.is_SUCCESS)

        self.assertEqual(card.type, cards.CARD.CHANGE_HABIT_LEGENDARY)
        self.assertEqual(combined_card_1.data, card.data)

    def test_get_combined_card_3__random(self):
        card, result = logic.get_combined_card(allow_premium_cards=True,
                                               combined_cards=(self.create_card(cards.CARD.CHANGE_HABIT_EPIC),
                                                               self.create_card(cards.CARD.CHANGE_HABIT_EPIC),
                                                               self.create_card(cards.CARD.ADD_EXPERIENCE_EPIC)))
        self.assertNotEqual(card, None)
        self.assertTrue(card.type.rarity.is_LEGENDARY)
        self.assertTrue(result.is_SUCCESS)

    def test_combine_3_legendary(self):
        card, result = logic.get_combined_card(allow_premium_cards=True,
                                               combined_cards=(self.create_card(cards.CARD.CHANGE_HABIT_LEGENDARY),
                                                               self.create_card(cards.CARD.CHANGE_HABIT_LEGENDARY),
                                                               self.create_card(cards.CARD.ADD_EXPERIENCE_LEGENDARY)))
        self.assertEqual(card, None)
        self.assertTrue(result.is_COMBINE_3_LEGENDARY)

    def test_combine_too_many_cards(self):
        card, result = logic.get_combined_card(allow_premium_cards=True,
                                               combined_cards=(self.create_card(cards.CARD.CHANGE_HABIT_EPIC),
                                                               self.create_card(cards.CARD.CHANGE_HABIT_EPIC),
                                                               self.create_card(cards.CARD.CHANGE_HABIT_EPIC),
                                                               self.create_card(cards.CARD.CHANGE_HABIT_EPIC)))
        self.assertEqual(card, None)
        self.assertTrue(result.is_TOO_MANY_CARDS)

    def test_allow_premium_cards__allowed(self):
        availability = set()

        for i in range(1000):
            card, result = logic.get_combined_card(allow_premium_cards=True,
                                                   combined_cards=(self.create_card(cards.CARD.CHANGE_HABIT_EPIC),
                                                                   self.create_card(cards.CARD.CHANGE_HABIT_EPIC),
                                                                   self.create_card(cards.CARD.ADD_EXPERIENCE_EPIC)))
            availability.add(card.type.availability)

        self.assertEqual(availability, set(relations.AVAILABILITY.records))

    def test_allow_premium_cards__not_allowed(self):
        availability = set()

        for i in range(1000):
            card, result = logic.get_combined_card(allow_premium_cards=False,
                                                   combined_cards=(self.create_card(cards.CARD.CHANGE_HABIT_EPIC),
                                                                   self.create_card(cards.CARD.CHANGE_HABIT_EPIC),
                                                                   self.create_card(cards.CARD.ADD_EXPERIENCE_EPIC)))
            availability.add(card.type.availability)

        self.assertEqual(availability, {relations.AVAILABILITY.FOR_ALL})

    def test_available_for_auction__available(self):
        card, result = logic.get_combined_card(allow_premium_cards=True,
                                               combined_cards=(self.create_card(cards.CARD.CHANGE_HABIT_EPIC),
                                                               self.create_card(cards.CARD.CHANGE_HABIT_EPIC),
                                                               self.create_card(cards.CARD.ADD_EXPERIENCE_EPIC)))
        self.assertTrue(card.available_for_auction)

    def test_available_for_auction__not_available(self):
        card, result = logic.get_combined_card(allow_premium_cards=True,
                                               combined_cards=(self.create_card(cards.CARD.CHANGE_HABIT_EPIC),
                                                               self.create_card(cards.CARD.CHANGE_HABIT_EPIC, available_for_auction=False),
                                                               self.create_card(cards.CARD.ADD_EXPERIENCE_EPIC)))
        self.assertFalse(card.available_for_auction)
