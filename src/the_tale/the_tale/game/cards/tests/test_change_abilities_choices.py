
import smart_imports

smart_imports.all()


class ChangeAbilitiesChoicesTest(utils_testcase.TestCase, helpers.CardsTestMixin):
    CARD = types.CARD.CHANGE_ABILITIES_CHOICES

    def setUp(self):
        super(ChangeAbilitiesChoicesTest, self).setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1.id)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

    def test_use(self):
        self.assertTrue(self.hero.abilities.can_rechoose_abilities_choices())

        with mock.patch('the_tale.game.logic_storage.LogicStorage.save_bundle_data') as save_bundle_data:
            with self.check_changed(lambda: self.hero.abilities.destiny_points_spend):
                result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))

        self.assertEqual(save_bundle_data.call_count, 1)

        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

    @mock.patch('the_tale.game.heroes.abilities.AbilitiesPrototype.can_rechoose_abilities_choices', lambda self: False)
    def test_can_not_rechose(self):
        self.assertFalse(self.hero.abilities.can_rechoose_abilities_choices())

        with self.check_not_changed(lambda: self.hero.abilities.destiny_points_spend):
            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))

        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))
