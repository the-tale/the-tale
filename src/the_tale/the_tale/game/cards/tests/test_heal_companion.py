
import random

from unittest import mock

from the_tale.common.utils import testcase

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.cards import cards

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.companions import storage as companions_storage
from the_tale.game.companions import logic as companions_logic

from the_tale.game.cards.tests.helpers import CardsTestMixin


class HealCompanionTestMixin(CardsTestMixin):
    CARD = None

    def setUp(self):
        super(HealCompanionTestMixin, self).setUp()
        create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        self.hero.set_companion(companions_logic.create_companion(random.choice(companions_storage.companions.all())))


    @mock.patch('the_tale.game.companions.objects.Companion.max_health', 666)
    def test_use(self):
        self.hero.companion.health = 1

        with self.check_delta(lambda: self.hero.companion.health, min(self.CARD.effect.modificator, self.hero.companion.max_health-1)):
            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
            self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

    def test_no_companion(self):
        self.hero.remove_companion()

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))

    def test_maximum_health(self):
        self.assertEqual(self.hero.companion.health, self.hero.companion.max_health)

        with self.check_not_changed(lambda: self.hero.companion.health):
            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
            self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))


class HealCompanionCommonTests(HealCompanionTestMixin, testcase.TestCase):
    CARD = cards.CARD.HEAL_COMPANION_COMMON


class HealCompanionUncommonTests(HealCompanionTestMixin, testcase.TestCase):
    CARD = cards.CARD.HEAL_COMPANION_UNCOMMON


class HealCompanionRareTests(HealCompanionTestMixin, testcase.TestCase):
    CARD = cards.CARD.HEAL_COMPANION_RARE


class HealCompanionEpicTests(HealCompanionTestMixin, testcase.TestCase):
    CARD = cards.CARD.HEAL_COMPANION_EPIC
