# coding: utf-8
import mock

from the_tale.common.utils.testcase import TestCase
from the_tale.common.postponed_tasks import FakePostpondTaskPrototype, POSTPONED_TASK_LOGIC_RESULT

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic import create_test_map
from the_tale.game.logic_storage import LogicStorage

from the_tale.game.cards.relations import CARD_TYPE
from the_tale.game.cards.prototypes import CARDS

from the_tale.game.heroes.postponed_tasks import CombineCardsTask
from the_tale.game.heroes import relations


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
        task = CombineCardsTask(self.hero.id, cards=[CARD_TYPE.LEVEL_UP]*2, card=CARD_TYPE.ADD_GOLD_COMMON)
        self.assertEqual(task.serialize(), CombineCardsTask.deserialize(task.serialize()).serialize())


    def test__can_not_combine(self):
        for combine_status in relations.CARDS_COMBINING_STATUS.records:
            if combine_status.is_ALLOWED:
                continue

            task = CombineCardsTask(self.hero.id, cards=[])

            with mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.can_combine_cards', lambda self, cards: combine_status):
                with self.check_not_changed(self.hero.cards.cards_count):
                    self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)

        self.assertFalse(self.hero.cards.has_cards)
        self.assertTrue(task.state.is_CAN_NOT_COMBINE)


    def test_success__2_cards(self):
        self.hero.cards.add_card(CARD_TYPE.ADD_GOLD_COMMON, 2)
        task = CombineCardsTask(self.hero.id, cards=[CARD_TYPE.ADD_GOLD_COMMON]*2)

        with self.check_delta(self.hero.cards.cards_count, -1):
            self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertTrue(self.hero.cards.has_cards)
        self.assertEqual(self.hero.cards.cards_count(), 1)

        self.assertTrue(self.hero.cards.cards[0][0].rarity.is_COMMON)

        self.assertTrue(self.hero.cards.cards[0][0].text.lower() in task.processed_data['message'].lower())
        self.assertTrue(CARDS[self.hero.cards.cards[0][0]].DESCRIPTION.lower() in task.processed_data['message'].lower())

        self.assertTrue(task.state.is_PROCESSED)

    def test_success__3_cards(self):
        self.hero.cards.add_card(CARD_TYPE.ADD_GOLD_COMMON, 3)
        task = CombineCardsTask(self.hero.id, cards=[CARD_TYPE.ADD_GOLD_COMMON]*3)

        with self.check_delta(self.hero.cards.cards_count, -2):
            self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertTrue(self.hero.cards.has_cards)

        self.assertTrue(self.hero.cards.cards[0][0].rarity.is_UNCOMMON)

        self.assertTrue(self.hero.cards.cards[0][0].text.lower() in task.processed_data['message'].lower())
        self.assertTrue(CARDS[self.hero.cards.cards[0][0]].DESCRIPTION.lower() in task.processed_data['message'].lower())

        self.assertTrue(task.state.is_PROCESSED)

    def test_success__remove_cards(self):
        self.hero.cards.add_card(CARD_TYPE.ADD_GOLD_COMMON, 1)
        self.hero.cards.add_card(CARD_TYPE.ADD_EXPERIENCE_COMMON, 2)
        self.hero.cards.add_card(CARD_TYPE.ADD_BONUS_ENERGY_COMMON, 1)
        self.hero.cards.add_card(CARD_TYPE.CHANGE_HERO_SPENDINGS_TO_INSTANT_HEAL, 1)
        self.hero.cards.add_card(CARD_TYPE.LEVEL_UP, 1)

        task = CombineCardsTask(self.hero.id, cards=[CARD_TYPE.ADD_GOLD_COMMON, CARD_TYPE.ADD_EXPERIENCE_COMMON, CARD_TYPE.ADD_BONUS_ENERGY_COMMON])

        with self.check_delta(self.hero.cards.cards_count, -2):
            self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertEqual(self.hero.cards.card_count(CARD_TYPE.ADD_GOLD_COMMON), 0)
        self.assertEqual(self.hero.cards.card_count(CARD_TYPE.ADD_EXPERIENCE_COMMON), 1)
        self.assertEqual(self.hero.cards.card_count(CARD_TYPE.ADD_BONUS_ENERGY_COMMON), 0)
        self.assertEqual(self.hero.cards.card_count(CARD_TYPE.CHANGE_HERO_SPENDINGS_TO_INSTANT_HEAL), 1)
        self.assertEqual(self.hero.cards.card_count(CARD_TYPE.LEVEL_UP), 1)

        self.assertTrue(task.state.is_PROCESSED)

    def test_success__remove_duplicates(self):
        self.hero.cards.add_card(CARD_TYPE.ADD_GOLD_COMMON, 3)
        self.hero.cards.add_card(CARD_TYPE.ADD_EXPERIENCE_COMMON, 2)
        self.hero.cards.add_card(CARD_TYPE.ADD_BONUS_ENERGY_COMMON, 1)
        self.hero.cards.add_card(CARD_TYPE.CHANGE_HERO_SPENDINGS_TO_INSTANT_HEAL, 1)
        self.hero.cards.add_card(CARD_TYPE.LEVEL_UP, 1)

        task = CombineCardsTask(self.hero.id, cards=[CARD_TYPE.ADD_GOLD_COMMON, CARD_TYPE.ADD_GOLD_COMMON, CARD_TYPE.ADD_BONUS_ENERGY_COMMON])

        with self.check_delta(self.hero.cards.cards_count, -2):
            self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertEqual(self.hero.cards.card_count(CARD_TYPE.ADD_GOLD_COMMON), 1)
        self.assertEqual(self.hero.cards.card_count(CARD_TYPE.ADD_EXPERIENCE_COMMON), 2)
        self.assertEqual(self.hero.cards.card_count(CARD_TYPE.ADD_BONUS_ENERGY_COMMON), 0)
        self.assertEqual(self.hero.cards.card_count(CARD_TYPE.CHANGE_HERO_SPENDINGS_TO_INSTANT_HEAL), 1)
        self.assertEqual(self.hero.cards.card_count(CARD_TYPE.LEVEL_UP), 1)

        self.assertTrue(task.state.is_PROCESSED)
