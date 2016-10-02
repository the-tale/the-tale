# coding: utf-8
from the_tale.common.utils.testcase import TestCase
from the_tale.common.postponed_tasks.prototypes import POSTPONED_TASK_LOGIC_RESULT
from the_tale.common.postponed_tasks.tests.helpers import FakePostpondTaskPrototype

from the_tale.game.balance import constants as c

from the_tale.game.logic import create_test_map
from the_tale.game.logic_storage import LogicStorage

from the_tale.game.heroes.postponed_tasks import GetCardTask


class GetCardTaskTest(TestCase):

    def setUp(self):
        super(GetCardTaskTest, self).setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)

        self.hero = self.storage.accounts_to_heroes[self.account.id]

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

        self.assertTrue(next(iter(self.hero.cards.all_cards())).name.lower() in task.processed_data['message'].lower())
        self.assertTrue(next(iter(self.hero.cards.all_cards())).effect.DESCRIPTION.lower() in task.processed_data['message'].lower())

        self.assertTrue(task.state.is_PROCESSED)
