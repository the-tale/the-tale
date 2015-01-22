# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.cards import effects

from the_tale.game.postponed_tasks import ComplexChangeTask
from the_tale.game.quests.logic import create_random_quest_for_hero
from the_tale.game.actions.prototypes import ActionQuestPrototype

from the_tale.game.cards.tests.helpers import CardsTestMixin


class AddPowerTestMixin(CardsTestMixin):
    CARD = None

    def setUp(self):
        super(AddPowerTestMixin, self).setUp()
        create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        self.card = self.CARD()

    def test_use(self):
        self.quest = create_random_quest_for_hero(self.hero)
        self.action_quest = ActionQuestPrototype.create(hero=self.hero, quest=self.quest)

        self.assertTrue(self.hero.quests.has_quests)

        with mock.patch('the_tale.game.quests.container.QuestsContainer.mark_updated') as mark_updated:
            with self.check_not_changed(lambda: self.hero.power):
                with self.check_not_changed(lambda: self.hero.level):
                    with self.check_not_changed(lambda: self.hero.quests.current_quest.current_info.power):
                        with self.check_delta(lambda: self.hero.quests.current_quest.current_info.power_bonus, self.CARD.POWER):
                            result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero=self.hero))
                            self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(mark_updated.call_count, 1)

    def test_no_quest(self):
        self.assertFalse(self.hero.quests.has_quests)

        result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero=self.hero))
        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))


class AddPowercommonTests(AddPowerTestMixin, testcase.TestCase):
    CARD = effects.AddPowerCommon


class AddPowerUncommonTests(AddPowerTestMixin, testcase.TestCase):
    CARD = effects.AddPowerUncommon


class AddPowerRareTests(AddPowerTestMixin, testcase.TestCase):
    CARD = effects.AddPowerRare


class AddPowerEpicTests(AddPowerTestMixin, testcase.TestCase):
    CARD = effects.AddPowerEpic
