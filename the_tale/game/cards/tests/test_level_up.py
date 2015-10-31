# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user
from the_tale.game.logic_storage import LogicStorage

from the_tale.game.logic import create_test_map

from the_tale.game.cards.effects import LevelUp

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.heroes import logic as heroes_logic

from the_tale.game.cards.tests.helpers import CardsTestMixin


class LevelUpTest(testcase.TestCase, CardsTestMixin):
    CARD = LevelUp

    def setUp(self):
        super(LevelUpTest, self).setUp()
        create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        self.abilities = self.hero.abilities

        self.card = self.CARD()


    def test_use(self):

        self.hero.add_experience(self.hero.experience_to_next_level / 2)

        self.assertTrue(self.hero.experience > 0)
        self.assertEqual(self.hero.level, 1)

        with self.check_not_changed(lambda: self.hero.experience):
            with self.check_delta(lambda: self.hero.level, 1):
                result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero=self.hero))
                self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        saved_hero = heroes_logic.load_hero(hero_id=self.hero.id)
        self.assertEqual(saved_hero.abilities.destiny_points, self.abilities.destiny_points)
