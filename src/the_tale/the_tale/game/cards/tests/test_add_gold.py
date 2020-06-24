
import smart_imports

smart_imports.all()


class AddGoldTestMixin(helpers.CardsTestMixin):
    CARD = None

    def setUp(self):
        super(AddGoldTestMixin, self).setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1.id)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

    def test_use(self):
        with self.check_delta(lambda: self.hero.money, self.CARD.effect.modificator):
            with self.check_delta(lambda: self.hero.statistics.money_earned_from_help, self.CARD.effect.modificator):
                with self.check_delta(lambda: self.hero.statistics.money_earned, self.CARD.effect.modificator):
                    result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))

        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))


class AddGoldCommonTests(AddGoldTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_GOLD_COMMON


class AddGoldUncommonTests(AddGoldTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_GOLD_UNCOMMON


class AddGoldRareTests(AddGoldTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_GOLD_RARE
