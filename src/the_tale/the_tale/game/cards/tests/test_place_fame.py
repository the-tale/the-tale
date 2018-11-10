
import smart_imports

smart_imports.all()


class PlaceFameMixin(helpers.CardsTestMixin):
    CARD = None

    def setUp(self):
        super().setUp()

        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        game_tt_services.debug_clear_service()

    def get_fame(self):
        return places_logic.get_hero_popularity(self.hero.id).get_fame(self.place_1.id)

    def test_use(self):

        with self.check_delta(self.get_fame, self.CARD.effect.modificator):
            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage,
                                                                                        hero=self.hero, value=self.place_1.id))

        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

    def test_wrong_place(self):
        with self.check_not_changed(self.get_fame):
            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage,
                                                                                        hero=self.hero,
                                                                                        value=666))

        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))


class PlaceFameUncommonTests(PlaceFameMixin, utils_testcase.TestCase):
    CARD = types.CARD.MOST_COMMON_PLACES_UNCOMMON


class PlaceFameRareTests(PlaceFameMixin, utils_testcase.TestCase):
    CARD = types.CARD.MOST_COMMON_PLACES_RARE


class PlaceFameEpicTests(PlaceFameMixin, utils_testcase.TestCase):
    CARD = types.CARD.MOST_COMMON_PLACES_EPIC


class PlaceFameLegendaryTests(PlaceFameMixin, utils_testcase.TestCase):
    CARD = types.CARD.MOST_COMMON_PLACES_LEGENDARY
