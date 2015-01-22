# coding: utf-8
from the_tale.common.utils.testcase import TestCase
from the_tale.common.postponed_tasks import FakePostpondTaskPrototype, POSTPONED_TASK_LOGIC_RESULT

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.balance import constants as c

from the_tale.game.logic import create_test_map
from the_tale.game.logic_storage import LogicStorage

from the_tale.game.heroes.postponed_tasks import GetCardTask


class GetCardTaskTest(TestCase):

    def setUp(self):
        super(GetCardTaskTest, self).setUp()
        place_1, place_2, place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)

        self.hero = self.storage.accounts_to_heroes[account_id]

    def test_create(self):
        task = GetCardTask(self.hero.id)
        self.assertTrue(task.state.is_UNPROCESSED)

    def test_serialization(self):
        task = GetCardTask(self.hero.id)
        self.assertEqual(task.serialize(), GetCardTask.deserialize(task.serialize()).serialize())

    def test__can_not_get(self):
        self.hero.cards.change_help_count(c.CARDS_HELP_COUNT_TO_NEW_CARD - 1)
        task = GetCardTask(self.hero.id)

        with self.check_not_changed(lambda: self.hero.cards.help_count):
            self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)

        self.assertFalse(self.hero.cards.has_cards)
        self.assertTrue(task.state.is_CAN_NOT_GET)

    def test_success(self):
        self.hero.cards.change_help_count(c.CARDS_HELP_COUNT_TO_NEW_CARD + 1)
        task = GetCardTask(self.hero.id)

        with self.check_delta(lambda: self.hero.cards.help_count, -c.CARDS_HELP_COUNT_TO_NEW_CARD):
            self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertTrue(self.hero.cards.has_cards)

        self.assertTrue(self.hero.cards.all_cards().next().name.lower() in task.processed_data['message'].lower())
        self.assertTrue(self.hero.cards.all_cards().next().effect.DESCRIPTION.lower() in task.processed_data['message'].lower())

        self.assertTrue(task.state.is_PROCESSED)
