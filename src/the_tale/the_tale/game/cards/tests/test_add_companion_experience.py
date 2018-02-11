
import random

from the_tale.common.utils import testcase

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.cards import cards

from the_tale.game.postponed_tasks import ComplexChangeTask
from the_tale.game.companions import storage as companions_storage
from the_tale.game.companions import logic as companions_logic

from the_tale.game.cards.tests.helpers import CardsTestMixin


def companion_total_experience(companion):
    n = companion.coherence - 1

    if n == 0:
        return companion.experience

    return companion.experience + n * (n - 1) / 2


class AddCompanionExperienceTestMixin(CardsTestMixin):
    CARD = None

    def setUp(self):
        super(AddCompanionExperienceTestMixin, self).setUp()
        create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

    def test_use(self):
        companion_record = random.choice(companions_storage.companions.all())
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.assertFalse(self.hero.companion.is_dead)

        with self.check_increased(lambda: companion_total_experience(self.hero.companion)):
            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
            self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

    def test_use__coherence_restriction_does_not_work(self):
        companion_record = random.choice(companions_storage.companions.all())
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        # test that coherence restriction does not work
        self.hero.companion.experience = self.hero.companion.experience_to_next_level

        self.assertFalse(self.hero.companion.is_dead)

        with self.check_increased(lambda: self.hero.companion.coherence):
            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
            self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))


    def test_use__companion_is_dead(self):
        companion_record = random.choice(companions_storage.companions.all())
        self.hero.set_companion(companions_logic.create_companion(companion_record))
        self.hero.companion.health = 0

        self.assertTrue(self.hero.companion.is_dead)

        with self.check_increased(lambda: companion_total_experience(self.hero.companion)):
            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
            self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

    def test_no_companion(self):
        self.assertEqual(self.hero.companion, None)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))


class AddExperienceCommonTests(AddCompanionExperienceTestMixin, testcase.TestCase):
    CARD = cards.CARD.ADD_COMPANION_EXPERIENCE_COMMON


class AddExperienceUncommonTests(AddCompanionExperienceTestMixin, testcase.TestCase):
    CARD = cards.CARD.ADD_COMPANION_EXPERIENCE_UNCOMMON


class AddExperienceRareTests(AddCompanionExperienceTestMixin, testcase.TestCase):
    CARD = cards.CARD.ADD_COMPANION_EXPERIENCE_RARE


class AddExperienceEpicTests(AddCompanionExperienceTestMixin, testcase.TestCase):
    CARD = cards.CARD.ADD_COMPANION_EXPERIENCE_EPIC


class AddExperienceLegendaryTests(AddCompanionExperienceTestMixin, testcase.TestCase):
    CARD = cards.CARD.ADD_COMPANION_EXPERIENCE_LEGENDARY
