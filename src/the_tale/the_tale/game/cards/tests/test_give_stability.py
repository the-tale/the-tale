
import smart_imports

smart_imports.all()


class GiveStabilityMixin(helpers.CardsTestMixin):
    CARD = None

    def setUp(self):
        super(GiveStabilityMixin, self).setUp()

        places_tt_services.effects.cmd_debug_clear_service()

        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account(is_fast=True)

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1)
        self.storage.load_account_data(self.account_2)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        self.card = self.CARD.effect.create_card(type=self.CARD, available_for_auction=True)

    def test_use(self):

        with mock.patch('the_tale.game.balance.constants.PLACE_BASE_STABILITY', 0.25):
            self.place_1.refresh_attributes()

            self.assertLess(self.place_1.attrs.stability, 1.0 - self.CARD.effect.modificator)

            with self.check_almost_delta(lambda: self.place_1.attrs.stability, self.CARD.effect.modificator):
                result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(hero=self.hero,
                                                                                            card=self.card,
                                                                                            value=self.place_1.id))

        self.assertEqual((result, step, postsave_actions),
                         (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

    def test_use_for_wrong_place_id(self):
        with mock.patch('the_tale.game.balance.constants.PLACE_BASE_STABILITY', 0.25):
            self.place_1.refresh_attributes()

            self.assertLess(self.place_1.attrs.stability, 1.0 - self.CARD.effect.modificator)

            with self.check_not_changed(lambda: self.place_1.attrs.stability):
                self.assertEqual(self.CARD.effect.use(**self.use_attributes(hero=self.hero, value=666, storage=self.storage)),
                                 (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED,
                                  game_postponed_tasks.ComplexChangeTask.STEP.ERROR,
                                  ()))


class GiveStabilityUncommonTests(GiveStabilityMixin, utils_testcase.TestCase):
    CARD = types.CARD.GIVE_STABILITY_UNCOMMON


class GiveStabilityRareTests(GiveStabilityMixin, utils_testcase.TestCase):
    CARD = types.CARD.GIVE_STABILITY_RARE


class GiveStabilityEpicTests(GiveStabilityMixin, utils_testcase.TestCase):
    CARD = types.CARD.GIVE_STABILITY_EPIC


class GiveStabilityLegendaryTests(GiveStabilityMixin, utils_testcase.TestCase):
    CARD = types.CARD.GIVE_STABILITY_LEGENDARY
