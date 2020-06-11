
import smart_imports

smart_imports.all()


class ResetAbilitiesTest(utils_testcase.TestCase, helpers.CardsTestMixin):
    CARD = types.CARD.RESET_ABILITIES

    def setUp(self):
        super(ResetAbilitiesTest, self).setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1.id)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

    def test_use(self):
        self.hero.randomized_level_up(increment_level=True)

        self.assertFalse(self.hero.abilities.is_initial_state())

        with mock.patch('the_tale.game.logic_storage.LogicStorage.save_bundle_data') as save_bundle_data:
            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))

        self.assertTrue(self.hero.abilities.is_initial_state())

        self.assertEqual(save_bundle_data.call_count, 1)

        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

    def test_can_not_rechose(self):

        self.assertTrue(self.hero.abilities.is_initial_state())

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))

        self.assertTrue(self.hero.abilities.is_initial_state())

        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))
