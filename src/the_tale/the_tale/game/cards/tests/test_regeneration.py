
import smart_imports
smart_imports.all()


class RegenerateTests(helpers.CardsTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.REGENERATION

    def setUp(self):
        super().setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account.id)

        self.hero = self.storage.accounts_to_heroes[self.account.id]

    def check_alive_and_healthy(self):
        self.assertTrue(self.hero.is_alive)
        self.assertEqual(self.hero.health, self.hero.max_health)

    def test_alife_and_healthy(self):
        self.check_alive_and_healthy()

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
        self.assertEqual((result, step, postsave_actions),
                         (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))

    def test_use__resurrect(self):
        self.hero.kill()

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
        self.assertEqual((result, step, postsave_actions),
                         (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED,
                          game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS,
                          ()))

        self.check_alive_and_healthy()

    def test_use__heal(self):
        self.hero.health = 1

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
        self.assertEqual((result, step, postsave_actions),
                         (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED,
                          game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS,
                          ()))

        self.check_alive_and_healthy()
