
import smart_imports

smart_imports.all()


class KeepersGoodsMixin(helpers.CardsTestMixin):
    CARD = None

    def setUp(self):
        super(KeepersGoodsMixin, self).setUp()

        places_tt_services.effects.cmd_debug_clear_service()

        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account(is_fast=True)

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1.id)
        self.storage.load_account_data(self.account_2.id)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        self.card = self.CARD.effect.create_card(type=self.CARD, available_for_auction=True)

    def test_use(self):

        self.place_1.attrs.size = 10
        self.place_1.refresh_attributes()

        with self.check_almost_delta(lambda: round(self.place_1.attrs.production, 2), self.CARD.effect.modificator):
            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(hero=self.hero,
                                                                                        card=self.card,
                                                                                        value=self.place_1.id))

        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED,
                                                            game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS,
                                                            ()))

    def test_use_for_wrong_place_id(self):
        with self.check_not_changed(lambda: self.place_1.attrs.production):
            self.assertEqual(self.CARD.effect.use(**self.use_attributes(hero=self.hero, value=666, storage=self.storage)),
                             (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED,
                              game_postponed_tasks.ComplexChangeTask.STEP.ERROR,
                              ()))


class KeepersGoodsCommonTests(KeepersGoodsMixin, utils_testcase.TestCase):
    CARD = types.CARD.KEEPERS_GOODS_COMMON


class KeepersGoodsUncommonTests(KeepersGoodsMixin, utils_testcase.TestCase):
    CARD = types.CARD.KEEPERS_GOODS_UNCOMMON


class KeepersGoodsRareTests(KeepersGoodsMixin, utils_testcase.TestCase):
    CARD = types.CARD.KEEPERS_GOODS_RARE


class KeepersGoodsEpicTests(KeepersGoodsMixin, utils_testcase.TestCase):
    CARD = types.CARD.KEEPERS_GOODS_EPIC


class KeepersGoodsLegendaryTests(KeepersGoodsMixin, utils_testcase.TestCase):
    CARD = types.CARD.KEEPERS_GOODS_LEGENDARY
