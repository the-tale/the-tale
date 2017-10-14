
from the_tale.common.utils import testcase

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game import relations as game_relations

from the_tale.game.cards import cards

from the_tale.game.postponed_tasks import ComplexChangeTask
from the_tale.game.relations import HABIT_TYPE
from the_tale.game.balance import constants as c

from the_tale.game.cards.tests.helpers import CardsTestMixin


class ChangeHabitTestMixin(CardsTestMixin):

    def setUp(self):
        super(ChangeHabitTestMixin, self).setUp()

        create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]


    def habit_value(self, habit):
        if habit.is_HONOR:
            return self.hero.habit_honor.raw_value

        if habit.is_PEACEFULNESS:
            return self.hero.habit_peacefulness.raw_value


    def test_use(self):
        for habit in game_relations.HABIT_TYPE.records:
            for direction in (-1, 1):
                card = self.CARD.effect.create_card(type=self.CARD,
                                                    available_for_auction=True,
                                                    habit=habit,
                                                    direction=direction)

                self.hero.change_habits(habit, 2 * (-c.HABITS_BORDER if direction > 0 else c.HABITS_BORDER))

                with self.check_delta(lambda: self.habit_value(habit), direction * self.CARD.effect.modificator):
                    result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero, card=card))

                self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

    def test_no_effect(self):
        for habit in game_relations.HABIT_TYPE.records:
            for direction in (-1, 1):
                card = self.CARD.effect.create_card(type=self.CARD,
                                                    available_for_auction=True,
                                                    habit=habit,
                                                    direction=direction)

                self.hero.change_habits(habit, 2 * (-c.HABITS_BORDER if direction < 0 else c.HABITS_BORDER))

                with self.check_not_changed(lambda: self.habit_value(habit)):
                    result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero, card=card))

                self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))


class ChangeHabitCommonTests(ChangeHabitTestMixin, testcase.TestCase):
    CARD = cards.CARD.CHANGE_HABIT_COMMON

class ChangeHabitUncommonTests(ChangeHabitTestMixin, testcase.TestCase):
    CARD = cards.CARD.CHANGE_HABIT_UNCOMMON

class ChangeHabitRareTests(ChangeHabitTestMixin, testcase.TestCase):
    CARD = cards.CARD.CHANGE_HABIT_RARE

class ChangeHabitEpicTests(ChangeHabitTestMixin, testcase.TestCase):
    CARD = cards.CARD.CHANGE_HABIT_EPIC

class ChangeHabitLegendaryTests(ChangeHabitTestMixin, testcase.TestCase):
    CARD = cards.CARD.CHANGE_HABIT_LEGENDARY
