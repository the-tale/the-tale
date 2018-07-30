
import smart_imports

smart_imports.all()


class LevelUpTest(utils_testcase.TestCase, helpers.CardsTestMixin):
    CARD = types.CARD.LEVEL_UP

    def setUp(self):
        super(LevelUpTest, self).setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
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
                self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

        saved_hero = heroes_logic.load_hero(hero_id=self.hero.id)
        self.assertEqual(saved_hero.abilities.destiny_points, self.abilities.destiny_points)
