# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.cards import prototypes

from the_tale.game.postponed_tasks import ComplexChangeTask
from the_tale.game.relations import HABIT_TYPE
from the_tale.game.balance import constants as c

from the_tale.game.cards.tests.helpers import CardsTestMixin


class ChangeHabitTestMixin(CardsTestMixin):
    CARD = None

    def setUp(self):
        super(ChangeHabitTestMixin, self).setUp()
        create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        self.card = self.CARD()

        self.hero.change_habits(HABIT_TYPE.HONOR, -c.HABITS_BORDER if self.CARD.POINTS > 0 else c.HABITS_BORDER)
        self.hero.change_habits(HABIT_TYPE.PEACEFULNESS, -c.HABITS_BORDER if self.CARD.POINTS > 0 else c.HABITS_BORDER)

    def habit_value(self):
        if self.card.HABIT.is_HONOR:
            return self.hero.habit_honor.raw_value

        if self.card.HABIT.is_PEACEFULNESS:
            return self.hero.habit_peacefulness.raw_value

    def test_use(self):
        with self.check_delta(self.habit_value, self.CARD.POINTS):
            result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero=self.hero))

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))


class ChangeHabitHonorPlusUncommonTests(ChangeHabitTestMixin, testcase.TestCase):
    CARD = prototypes.ChangeHabitHonorPlusUncommon

class ChangeHabitHonorMinusUncommonTests(ChangeHabitTestMixin, testcase.TestCase):
    CARD = prototypes.ChangeHabitHonorMinusUncommon

class ChangeHabitPeacefulnessPlusUncommonTests(ChangeHabitTestMixin, testcase.TestCase):
    CARD = prototypes.ChangeHabitPeacefulnessPlusUncommon

class ChangeHabitPeacefulnessMinusUncommonTests(ChangeHabitTestMixin, testcase.TestCase):
    CARD = prototypes.ChangeHabitPeacefulnessMinusUncommon

class ChangeHabitHonorPlusRareTests(ChangeHabitTestMixin, testcase.TestCase):
    CARD = prototypes.ChangeHabitHonorPlusRare

class ChangeHabitHonorMinusRareTests(ChangeHabitTestMixin, testcase.TestCase):
    CARD = prototypes.ChangeHabitHonorMinusRare

class ChangeHabitPeacefulnessPlusRareTests(ChangeHabitTestMixin, testcase.TestCase):
    CARD = prototypes.ChangeHabitPeacefulnessPlusRare

class ChangeHabitPeacefulnessMinusRareTests(ChangeHabitTestMixin, testcase.TestCase):
    CARD = prototypes.ChangeHabitPeacefulnessMinusRare

class ChangeHabitHonorPlusEpicTests(ChangeHabitTestMixin, testcase.TestCase):
    CARD = prototypes.ChangeHabitHonorPlusEpic

class ChangeHabitHonorMinusEpicTests(ChangeHabitTestMixin, testcase.TestCase):
    CARD = prototypes.ChangeHabitHonorMinusEpic

class ChangeHabitPeacefulnessPlusEpicTests(ChangeHabitTestMixin, testcase.TestCase):
    CARD = prototypes.ChangeHabitPeacefulnessPlusEpic

class ChangeHabitPeacefulnessMinusEpicTests(ChangeHabitTestMixin, testcase.TestCase):
    CARD = prototypes.ChangeHabitPeacefulnessMinusEpic

class ChangeHabitHonorPlusLegendaryTests(ChangeHabitTestMixin, testcase.TestCase):
    CARD = prototypes.ChangeHabitHonorPlusLegendary

class ChangeHabitHonorMinusLegendaryTests(ChangeHabitTestMixin, testcase.TestCase):
    CARD = prototypes.ChangeHabitHonorMinusLegendary

class ChangeHabitPeacefulnessPlusLegendaryTests(ChangeHabitTestMixin, testcase.TestCase):
    CARD = prototypes.ChangeHabitPeacefulnessPlusLegendary

class ChangeHabitPeacefulnessMinusLegendaryTests(ChangeHabitTestMixin, testcase.TestCase):
    CARD = prototypes.ChangeHabitPeacefulnessMinusLegendary
