
import smart_imports

smart_imports.all()


class ReleaseCompanionTests(helpers.CardsTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.RELEASE_COMPANION

    def setUp(self):
        super(ReleaseCompanionTests, self).setUp()
        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        self.card = self.CARD.effect.create_card(type=self.CARD, available_for_auction=True)

    def test_use__has_companion(self):
        old_companion_record = random.choice(companions_storage.companions.all())
        self.hero.set_companion(companions_logic.create_companion(old_companion_record))

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero, card=self.card))

        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(self.hero.companion, None)

    def test_use__no_companion_exists(self):

        self.assertEqual(self.hero.companion, None)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero, card=self.card))
        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))

        self.assertEqual(self.hero.companion, None)
