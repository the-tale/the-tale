
from unittest import mock

from the_tale.common.utils import testcase

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.cards import cards

from the_tale.game.postponed_tasks import ComplexChangeTask
from the_tale.game.quests.tests import helpers as quests_helpers
from the_tale.game.actions.prototypes import ActionQuestPrototype

from the_tale.game.cards.tests.helpers import CardsTestMixin


class AddPoliticPowerTestMixin(CardsTestMixin):
    CARD = None

    def setUp(self):
        super(AddPoliticPowerTestMixin, self).setUp()

        create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]


    def test_use(self):
        self.action_quest = ActionQuestPrototype.create(hero=self.hero)
        quests_helpers.setup_quest(self.hero)

        self.assertTrue(self.hero.quests.has_quests)

        with mock.patch('the_tale.game.quests.container.QuestsContainer.mark_updated') as mark_updated:
            with self.check_not_changed(lambda: self.hero.power):
                with self.check_not_changed(lambda: self.hero.level):
                    with self.check_not_changed(lambda: self.hero.quests.current_quest.current_info.power):
                        with self.check_delta(lambda: self.hero.quests.current_quest.current_info.power_bonus, self.CARD.effect.modificator):
                            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
                            self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(mark_updated.call_count, 1)

    def test_no_quest(self):
        self.assertFalse(self.hero.quests.has_quests)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))


class AddPoliticPowerCommonTests(AddPoliticPowerTestMixin, testcase.TestCase):
    CARD = cards.CARD.ADD_POWER_COMMON


class AddPoliticPowerUncommonTests(AddPoliticPowerTestMixin, testcase.TestCase):
    CARD = cards.CARD.ADD_POWER_UNCOMMON


class AddPoliticPowerRareTests(AddPoliticPowerTestMixin, testcase.TestCase):
    CARD = cards.CARD.ADD_POWER_RARE


class AddPoliticPowerEpicTests(AddPoliticPowerTestMixin, testcase.TestCase):
    CARD = cards.CARD.ADD_POWER_EPIC


class AddPoliticPowerLegendaryTests(AddPoliticPowerTestMixin, testcase.TestCase):
    CARD = cards.CARD.ADD_POWER_LEGENDARY
