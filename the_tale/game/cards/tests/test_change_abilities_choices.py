# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user
from the_tale.game.logic_storage import LogicStorage

from the_tale.game.logic import create_test_map

from the_tale.game.cards import prototypes

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.cards.tests.helpers import CardsTestMixin


class ChangeAbilitiesChoicesTest(testcase.TestCase, CardsTestMixin):
    CARD = prototypes.ChangeAbilitiesChoices

    def setUp(self):
        super(ChangeAbilitiesChoicesTest, self).setUp()
        create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        self.card = self.CARD()


    def test_use(self):
        self.assertTrue(self.hero.abilities.can_rechoose_abilities_choices())

        with self.check_changed(lambda: self.hero.abilities.destiny_points_spend):
            result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero=self.hero))

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))


    @mock.patch('the_tale.game.heroes.habilities.AbilitiesPrototype.can_rechoose_abilities_choices', lambda self: False)
    def test_can_not_rechose(self):
        self.assertFalse(self.hero.abilities.can_rechoose_abilities_choices())

        with self.check_not_changed(lambda: self.hero.abilities.destiny_points_spend):
            result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero=self.hero))

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))
