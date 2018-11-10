
import smart_imports

smart_imports.all()


class AddBonusEnergyTestMixin(helpers.CardsTestMixin):
    CARD = None

    def setUp(self):
        super(AddBonusEnergyTestMixin, self).setUp()
        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

    def test_use(self):
        with self.check_delta(lambda: game_tt_services.energy.cmd_balance(self.account_1.id), self.CARD.effect.modificator):
            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
            time.sleep(0.1)

        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))


class AddBonusEnergyCommonTests(AddBonusEnergyTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_BONUS_ENERGY_COMMON


class AddBonusEnergyUncommonTests(AddBonusEnergyTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_BONUS_ENERGY_UNCOMMON


class AddBonusEnergyRareTests(AddBonusEnergyTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_BONUS_ENERGY_RARE


class AddBonusEnergyEpicTests(AddBonusEnergyTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_BONUS_ENERGY_EPIC


class AddBonusEnergyLegendaryTests(AddBonusEnergyTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_BONUS_ENERGY_LEGENDARY
