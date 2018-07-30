
import smart_imports

smart_imports.all()


class SharpRandomArtifactTests(helpers.CardsTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.SHARP_RANDOM_ARTIFACT

    def setUp(self):
        super(SharpRandomArtifactTests, self).setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

    def test_use(self):
        with self.check_delta(lambda: self.hero.equipment.get_power().total(), 1):
            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))

        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))


class SharpAllArtifactsTests(helpers.CardsTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.SHARP_ALL_ARTIFACTS

    def setUp(self):
        super(SharpAllArtifactsTests, self).setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

    def test_use(self):
        with self.check_delta(lambda: self.hero.equipment.get_power().total(), len(list(self.hero.equipment.values()))):
            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))

        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))
