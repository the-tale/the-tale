
import smart_imports

smart_imports.all()


class AddPlacePowerMixin(helpers.CardsTestMixin):
    CARD = None

    def setUp(self):
        super(AddPlacePowerMixin, self).setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        amqp_environment.environment.deinitialize()
        amqp_environment.environment.initialize()

        self.highlevel = amqp_environment.environment.workers.highlevel
        self.highlevel.process_initialize(0, 'highlevel')

    def test_use(self):
        for direction in (-1, 1):
            game_tt_services.debug_clear_service()

            card = self.CARD.effect.create_card(type=self.CARD,
                                                available_for_auction=True,
                                                direction=direction)

            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(hero=self.hero,
                                                                                        storage=self.storage,
                                                                                        value=self.place_1.id,
                                                                                        card=card))

            self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

            impacts = politic_power_logic.get_last_power_impacts(limit=100)

            self.assertEqual(len(impacts), 1)

            self.assertEqual(impacts[0].amount, direction * self.CARD.effect.modificator)
            self.assertTrue(impacts[0].type.is_INNER_CIRCLE)
            self.assertTrue(impacts[0].target_type.is_PLACE)
            self.assertEqual(impacts[0].target_id, self.place_1.id)
            self.assertTrue(impacts[0].actor_type.is_HERO)
            self.assertEqual(impacts[0].actor_id, self.hero.id)

    def test_no_place(self):
        for direction in (-1, 1):
            card = self.CARD.effect.create_card(type=self.CARD,
                                                available_for_auction=True,
                                                direction=direction)

            self.assertEqual(self.CARD.effect.use(**self.use_attributes(hero=self.hero, value=666, storage=self.storage, card=card)),
                             (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))


class AddPlacePowerCommonTests(AddPlacePowerMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_PLACE_POWER_COMMON


class AddPlacePowerUncommonTests(AddPlacePowerMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_PLACE_POWER_UNCOMMON


class AddPlacePowerRareTests(AddPlacePowerMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_PLACE_POWER_RARE


class AddPlacePowerEpicTests(AddPlacePowerMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_PLACE_POWER_EPIC


class AddPlacePowerLegendaryTests(AddPlacePowerMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_PLACE_POWER_LEGENDARY
