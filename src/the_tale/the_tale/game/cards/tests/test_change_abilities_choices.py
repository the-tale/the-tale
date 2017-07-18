
from unittest import mock

from the_tale.common.utils import testcase

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.logic import create_test_map

from the_tale.game.cards import cards

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.cards.tests.helpers import CardsTestMixin


class ChangeAbilitiesChoicesTest(testcase.TestCase, CardsTestMixin):
    CARD = cards.CARD.CHANGE_ABILITIES_CHOICES

    def setUp(self):
        super(ChangeAbilitiesChoicesTest, self).setUp()

        create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]


    def test_use(self):
        self.assertTrue(self.hero.abilities.can_rechoose_abilities_choices())

        with mock.patch('the_tale.game.logic_storage.LogicStorage.save_bundle_data') as save_bundle_data:
            with self.check_changed(lambda: self.hero.abilities.destiny_points_spend):
                result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))

        self.assertEqual(save_bundle_data.call_count, 1)

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))


    @mock.patch('the_tale.game.heroes.habilities.AbilitiesPrototype.can_rechoose_abilities_choices', lambda self: False)
    def test_can_not_rechose(self):
        self.assertFalse(self.hero.abilities.can_rechoose_abilities_choices())

        with self.check_not_changed(lambda: self.hero.abilities.destiny_points_spend):
            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))
