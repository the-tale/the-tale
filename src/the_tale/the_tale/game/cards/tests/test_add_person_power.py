
import smart_imports

smart_imports.all()


class AddPersonPowerMixin(helpers.CardsTestMixin):
    CARD = None

    def setUp(self):
        super(AddPersonPowerMixin, self).setUp()
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

            person = self.place_1.persons[0]

            result, step, postsave_actions = card.effect.use(**self.use_attributes(hero=self.hero,
                                                                                   storage=self.storage,
                                                                                   value=person.id,
                                                                                   card=card))
            self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

            impacts = politic_power_logic.get_last_power_impacts(limit=100)

            self.assertEqual(len(impacts), 1)

            self.assertEqual(impacts[0].amount, direction * self.CARD.effect.modificator)
            self.assertTrue(impacts[0].type.is_INNER_CIRCLE)
            self.assertTrue(impacts[0].target_type.is_PERSON)
            self.assertEqual(impacts[0].target_id, person.id)
            self.assertTrue(impacts[0].actor_type.is_HERO)
            self.assertEqual(impacts[0].actor_id, self.hero.id)

            impacts = politic_power_logic.get_last_power_impacts(limit=100, storages=[game_tt_services.job_impacts])

            self.assertEqual(len(impacts), 1)

            self.assertEqual(impacts[0].amount, self.CARD.effect.modificator)
            self.assertTrue(impacts[0].type.is_JOB)

            if direction > 0:
                self.assertTrue(impacts[0].target_type.is_JOB_PERSON_POSITIVE)
            else:
                self.assertTrue(impacts[0].target_type.is_JOB_PERSON_NEGATIVE)

            self.assertEqual(impacts[0].target_id, person.id)
            self.assertTrue(impacts[0].actor_type.is_HERO)
            self.assertEqual(impacts[0].actor_id, self.hero.id)

    def test_no_person(self):
        for direction in (-1, 1):
            card = self.CARD.effect.create_card(type=self.CARD,
                                                available_for_auction=True,
                                                direction=direction)

            self.assertEqual(self.CARD.effect.use(**self.use_attributes(hero=self.hero, value=666, storage=self.storage, card=card)),
                             (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))


class AddPersonPowerCommon(AddPersonPowerMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_PERSON_POWER_COMMON


class AddPersonPowerUncommon(AddPersonPowerMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_PERSON_POWER_UNCOMMON


class AddPersonPowerRare(AddPersonPowerMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_PERSON_POWER_RARE


class AddPersonPowerEpic(AddPersonPowerMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_PERSON_POWER_EPIC


class AddPersonPowerLegendary(AddPersonPowerMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_PERSON_POWER_LEGENDARY
