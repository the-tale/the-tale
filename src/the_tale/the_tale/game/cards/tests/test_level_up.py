
from the_tale.common.utils import testcase

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.logic import create_test_map

from the_tale.game.cards import cards

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.heroes import logic as heroes_logic

from the_tale.game.cards.tests.helpers import CardsTestMixin


class LevelUpTest(testcase.TestCase, CardsTestMixin):
    CARD = cards.CARD.LEVEL_UP

    def setUp(self):
        super(LevelUpTest, self).setUp()

        create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        self.abilities = self.hero.abilities


    def test_use(self):

        self.hero.add_experience(self.hero.experience_to_next_level / 2)

        self.assertTrue(self.hero.experience > 0)
        self.assertEqual(self.hero.level, 1)

        with self.check_not_changed(lambda: self.hero.experience):
            with self.check_delta(lambda: self.hero.level, 1):
                result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
                self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        saved_hero = heroes_logic.load_hero(hero_id=self.hero.id)
        self.assertEqual(saved_hero.abilities.destiny_points, self.abilities.destiny_points)
