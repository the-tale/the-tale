# coding: utf-8
import mock

from the_tale.common.utils.testcase import TestCase
from the_tale.common.postponed_tasks import FakePostpondTaskPrototype, POSTPONED_TASK_LOGIC_RESULT

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic import create_test_map
from the_tale.game.logic_storage import LogicStorage

from the_tale.game.cards import relations as cards_relations
from the_tale.game.cards import objects as cards_objects

from the_tale.game.heroes.postponed_tasks import CombineCardsTask


class CombineCardsTaskTest(TestCase):

    def setUp(self):
        super(CombineCardsTaskTest, self).setUp()
        place_1, place_2, place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)

        self.hero = self.storage.accounts_to_heroes[account_id]


    def test_create(self):
        task = CombineCardsTask(self.hero.id, cards=[])
        self.assertTrue(task.state.is_UNPROCESSED)


    def test_serialization(self):
        card_1 = cards_objects.Card(cards_relations.CARD_TYPE.ADD_GOLD_COMMON)
        card_2 = cards_objects.Card(cards_relations.CARD_TYPE.ADD_GOLD_COMMON)

        self.hero.cards.add_card(card_1)
        self.hero.cards.add_card(card_2)

        task = CombineCardsTask(self.hero.id, cards=[card_1.uid, card_2.uid], message='test message')
        self.assertEqual(task.serialize(), CombineCardsTask.deserialize(task.serialize()).serialize())


    def test__can_not_combine(self):
        for combine_status in cards_relations.CARDS_COMBINING_STATUS.records:
            if combine_status.is_ALLOWED:
                continue

            task = CombineCardsTask(self.hero.id, cards=[])

            with mock.patch('the_tale.game.cards.container.CardsContainer.can_combine_cards', lambda self, cards: combine_status):
                with self.check_not_changed(self.hero.cards.cards_count):
                    self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)

        self.assertFalse(self.hero.cards.has_cards)
        self.assertTrue(task.state.is_CAN_NOT_COMBINE)


    def test_success__2_cards(self):
        card_1 = cards_objects.Card(cards_relations.CARD_TYPE.ADD_GOLD_COMMON)
        card_2 = cards_objects.Card(cards_relations.CARD_TYPE.ADD_GOLD_COMMON)

        self.hero.cards.add_card(card_1)
        self.hero.cards.add_card(card_2)

        task = CombineCardsTask(self.hero.id, cards=[card_1.uid, card_2.uid])

        with self.check_delta(self.hero.cards.cards_count, -1):
            self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertTrue(self.hero.cards.has_cards)
        self.assertEqual(self.hero.cards.cards_count(), 1)

        self.assertTrue(self.hero.cards.all_cards().next().type.rarity.is_COMMON)

        self.assertTrue(self.hero.cards.all_cards().next().type.text.lower() in task.processed_data['message'].lower())
        self.assertTrue(self.hero.cards.all_cards().next().effect.DESCRIPTION.lower() in task.processed_data['message'].lower())

        self.assertTrue(task.state.is_PROCESSED)

    def test_success__3_cards(self):
        card_1 = cards_objects.Card(cards_relations.CARD_TYPE.ADD_GOLD_COMMON)
        card_2 = cards_objects.Card(cards_relations.CARD_TYPE.ADD_GOLD_COMMON)
        card_3 = cards_objects.Card(cards_relations.CARD_TYPE.ADD_GOLD_COMMON)

        self.hero.cards.add_card(card_1)
        self.hero.cards.add_card(card_2)
        self.hero.cards.add_card(card_3)

        task = CombineCardsTask(self.hero.id, cards=[card_1.uid, card_2.uid, card_3.uid])

        with self.check_delta(self.hero.cards.cards_count, -2):
            self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertTrue(self.hero.cards.has_cards)

        self.assertTrue(self.hero.cards.all_cards().next().type.rarity.is_UNCOMMON)

        self.assertTrue(self.hero.cards.all_cards().next().name.lower() in task.processed_data['message'].lower())
        self.assertTrue(self.hero.cards.all_cards().next().effect.DESCRIPTION.lower() in task.processed_data['message'].lower())

        self.assertTrue(task.state.is_PROCESSED)

    def test_success__remove_cards(self):
        cards = [cards_objects.Card(cards_relations.CARD_TYPE.ADD_GOLD_COMMON),
                 cards_objects.Card(cards_relations.CARD_TYPE.ADD_EXPERIENCE_COMMON),
                 cards_objects.Card(cards_relations.CARD_TYPE.ADD_EXPERIENCE_COMMON),
                 cards_objects.Card(cards_relations.CARD_TYPE.ADD_BONUS_ENERGY_COMMON),
                 cards_objects.Card(cards_relations.CARD_TYPE.CHANGE_HERO_SPENDINGS_TO_INSTANT_HEAL),
                 cards_objects.Card(cards_relations.CARD_TYPE.LEVEL_UP) ]

        for card in cards:
            self.hero.cards.add_card(card)

        task = CombineCardsTask(self.hero.id, cards=[cards[0].uid, cards[2].uid, cards[3].uid])

        with self.check_delta(self.hero.cards.cards_count, -2):
            self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertFalse(self.hero.cards.has_card(cards[0].uid))
        self.assertTrue(self.hero.cards.has_card(cards[1].uid))
        self.assertFalse(self.hero.cards.has_card(cards[2].uid))
        self.assertFalse(self.hero.cards.has_card(cards[3].uid))
        self.assertTrue(self.hero.cards.has_card(cards[4].uid))
        self.assertTrue(self.hero.cards.has_card(cards[5].uid))

        self.assertTrue(task.state.is_PROCESSED)

    def test_success__remove_duplicates(self):
        cards = [cards_objects.Card(cards_relations.CARD_TYPE.ADD_GOLD_COMMON),
                 cards_objects.Card(cards_relations.CARD_TYPE.ADD_GOLD_COMMON),
                 cards_objects.Card(cards_relations.CARD_TYPE.ADD_GOLD_COMMON),
                 cards_objects.Card(cards_relations.CARD_TYPE.ADD_EXPERIENCE_COMMON),
                 cards_objects.Card(cards_relations.CARD_TYPE.ADD_EXPERIENCE_COMMON),
                 cards_objects.Card(cards_relations.CARD_TYPE.ADD_BONUS_ENERGY_COMMON),
                 cards_objects.Card(cards_relations.CARD_TYPE.CHANGE_HERO_SPENDINGS_TO_INSTANT_HEAL),
                 cards_objects.Card(cards_relations.CARD_TYPE.LEVEL_UP)]

        for card in cards:
            self.hero.cards.add_card(card)

        task = CombineCardsTask(self.hero.id, cards=[cards[1].uid, cards[2].uid, cards[5].uid])

        with self.check_delta(self.hero.cards.cards_count, -2):
            self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertTrue(self.hero.cards.has_card(cards[0].uid))
        self.assertFalse(self.hero.cards.has_card(cards[1].uid))
        self.assertFalse(self.hero.cards.has_card(cards[2].uid))
        self.assertTrue(self.hero.cards.has_card(cards[3].uid))
        self.assertTrue(self.hero.cards.has_card(cards[4].uid))
        self.assertFalse(self.hero.cards.has_card(cards[5].uid))
        self.assertTrue(self.hero.cards.has_card(cards[6].uid))
        self.assertTrue(self.hero.cards.has_card(cards[7].uid))

        self.assertTrue(task.state.is_PROCESSED)
