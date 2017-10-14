
from unittest import mock
import random

from the_tale.common.utils import testcase

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.cards import cards

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.companions import storage as companions_storage
from the_tale.game.companions import logic as companions_logic

from the_tale.game.heroes.relations import ITEMS_OF_EXPENDITURE

from . import helpers


class ChangeHeroSpendings(testcase.TestCase, helpers.CardsTestMixin):

    def setUp(self):
        super().setUp()

        create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        old_companion_record = random.choice(companions_storage.companions.all())
        self.hero.set_companion(companions_logic.create_companion(old_companion_record))


    def test_use(self):

        # sure that quests will be loaded and not cal mark_updated
        self.hero.quests.mark_updated()

        for item in ITEMS_OF_EXPENDITURE.records:
            card = cards.CARD.CHANGE_HERO_SPENDINGS.effect.create_card(type=cards.CARD.CHANGE_HERO_SPENDINGS,
                                                                       available_for_auction=True,
                                                                       item=item)

            while self.hero.next_spending == item:
                self.hero.switch_spending()

            with mock.patch('the_tale.game.quests.container.QuestsContainer.mark_updated') as mark_updated:
                result, step, postsave_actions = card.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero, card=card))

            self.assertEqual(mark_updated.call_count, 1)

            self.assertEqual(self.hero.next_spending, item)

            self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))


    def test_equal(self):
        card = cards.CARD.CHANGE_HERO_SPENDINGS.effect.create_card(type=cards.CARD.CHANGE_HERO_SPENDINGS,
                                                                   available_for_auction=True,
                                                                   item=self.hero.next_spending)

        with mock.patch('the_tale.game.quests.container.QuestsContainer.mark_updated') as mark_updated:
            result, step, postsave_actions = card.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero, card=card))

        self.assertEqual(mark_updated.call_count, 0)

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))


    def test_use__no_companion(self):
        self.hero.remove_companion()

        item = ITEMS_OF_EXPENDITURE.HEAL_COMPANION

        card = cards.CARD.CHANGE_HERO_SPENDINGS.effect.create_card(type=cards.CARD.CHANGE_HERO_SPENDINGS,
                                                                   available_for_auction=True,
                                                                   item=item)

        while self.hero.next_spending == item:
            self.hero.switch_spending()


        with mock.patch('the_tale.game.quests.container.QuestsContainer.mark_updated') as mark_updated:
            result, step, postsave_actions = card.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero, card=card))

        self.assertEqual(mark_updated.call_count, 0)

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))

        self.assertNotEqual(self.hero.next_spending, item)
