# coding: utf-8
from unittest import mock

from the_tale.common.utils import testcase

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.cards import effects

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.cards.tests.helpers import CardsTestMixin


class CancelQuestTests(CardsTestMixin, testcase.TestCase):
    CARD = effects.CancelQuest

    def setUp(self):
        super(CancelQuestTests, self).setUp()

        create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        self.card = self.CARD()

    def test_no_quests(self):
        self.assertFalse(self.hero.quests.has_quests)

        result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero=self.hero))
        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))

        self.assertFalse(self.hero.quests.has_quests)

    def test_use(self):
        self.hero.quests.push_quest('QUEST')
        self.assertTrue(self.hero.quests.has_quests)

        with mock.patch('the_tale.game.quests.container.QuestsContainer.mark_updated') as mark_updated:
            result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero=self.hero))

        self.assertEqual(mark_updated.call_count, 2)

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertFalse(self.hero.quests.has_quests)
