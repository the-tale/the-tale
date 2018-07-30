
import smart_imports

smart_imports.all()


class CalculatePowerFractionsTests(utils_testcase.TestCase):

    def test_no_powers(self):
        self.assertEqual(logic.calculate_power_fractions({}), {})

    def test_no_negative_powers(self):
        self.assertEqual(logic.calculate_power_fractions({1: 10 * 2,
                                                          2: 20 * 2,
                                                          3: 70 * 2}),
                         {1: 0.1,
                          2: 0.2,
                          3: 0.7})

    def test_with_negative_powers(self):
        self.assertEqual(logic.calculate_power_fractions({1: 10,
                                                          2: -20,
                                                          3: 70}),
                         {1: (10 + 20) / (10 + 20 + 70 + 20),
                          2: 0,
                          3: (70 + 20) / (10 + 20 + 70 + 20)})


class SyncPowerTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        game_tt_services.debug_clear_service()

        logic.add_power_impacts([game_tt_services.PowerImpact.hero_2_person(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                                            hero_id=1,
                                                                            person_id=10,
                                                                            amount=100),
                                 game_tt_services.PowerImpact.hero_2_person(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                                            hero_id=2,
                                                                            person_id=20,
                                                                            amount=200),
                                 game_tt_services.PowerImpact.hero_2_place(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                                           hero_id=1,
                                                                           place_id=30,
                                                                           amount=300),
                                 game_tt_services.PowerImpact.hero_2_place(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                                           hero_id=3,
                                                                           place_id=40,
                                                                           amount=400)])

    def test_success(self):

        with mock.patch('the_tale.game.politic_power.storage.PlacesPowerStorage.reset') as reset_places:
            with mock.patch('the_tale.game.politic_power.storage.PersonsPowerStorage.reset') as reset_persons:
                logic.sync_power()

        self.assertTrue(reset_places.called)
        self.assertTrue(reset_persons.called)

        targets = [(tt_api_impacts.OBJECT_TYPE.PERSON, 10),
                   (tt_api_impacts.OBJECT_TYPE.PERSON, 20),
                   (tt_api_impacts.OBJECT_TYPE.PLACE, 30),
                   (tt_api_impacts.OBJECT_TYPE.PLACE, 40)]

        impacts = game_tt_services.personal_impacts.cmd_get_targets_impacts(targets=targets)

        self.assertCountEqual([impact.amount for impact in impacts], [math.floor(100 * c.PLACE_POWER_REDUCE_FRACTION),
                                                                      math.floor(400 * c.PLACE_POWER_REDUCE_FRACTION)])

        impacts = game_tt_services.crowd_impacts.cmd_get_targets_impacts(targets=targets)

        self.assertCountEqual([impact.amount for impact in impacts], [math.floor(200 * c.PLACE_POWER_REDUCE_FRACTION),
                                                                      math.floor(300 * c.PLACE_POWER_REDUCE_FRACTION)])


class GetInnerCircleTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        game_tt_services.debug_clear_service()

        self.person_impacts = []
        self.place_impacts = []

        test_size = conf.settings.PLACE_INNER_CIRCLE_SIZE + conf.settings.PERSON_INNER_CIRCLE_SIZE

        self.person_id = 666
        self.place_id = 777

        for i in range(test_size):
            self.person_impacts.append(game_tt_services.PowerImpact.hero_2_person(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                                                  hero_id=100 + i,
                                                                                  person_id=self.person_id,
                                                                                  amount=1000 + i))
            self.person_impacts.append(game_tt_services.PowerImpact.hero_2_person(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                                                  hero_id=200 + i,
                                                                                  person_id=self.person_id,
                                                                                  amount=2000 + i))

        for i in range(test_size):
            self.place_impacts.append(game_tt_services.PowerImpact.hero_2_place(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                                                hero_id=300 + i,
                                                                                place_id=self.place_id,
                                                                                amount=3000 + i))
            self.place_impacts.append(game_tt_services.PowerImpact.hero_2_place(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                                                hero_id=400 + i,
                                                                                place_id=self.place_id,
                                                                                amount=4000 + i))

        logic.add_power_impacts(self.person_impacts)
        logic.add_power_impacts(self.place_impacts)

    def test_get_place_circle(self):
        circle = logic.get_inner_circle(place_id=self.place_id)
        self.assertEqual(circle.rating, [(309, 3009),
                                         (308, 3008),
                                         (307, 3007),
                                         (306, 3006),
                                         (305, 3005),
                                         (304, 3004),
                                         (303, 3003),
                                         (302, 3002),
                                         (301, 3001),
                                         (300, 3000)])

    def test_get_person_circle(self):
        circle = logic.get_inner_circle(person_id=self.person_id)
        self.assertEqual(circle.rating, [(109, 1009),
                                         (108, 1008),
                                         (107, 1007),
                                         (106, 1006),
                                         (105, 1005),
                                         (104, 1004),
                                         (103, 1003),
                                         (102, 1002),
                                         (101, 1001),
                                         (100, 1000)])

    def test_no_actor(self):
        self.assertRaises(NotImplementedError, logic.get_inner_circle)


class GetJobPowerTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        game_tt_services.debug_clear_service()

        impacts = []

        self.hero_id = 111
        self.person_id = 666
        self.place_id = 777

        impacts = [game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.JOB,
                                                actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                actor_id=self.hero_id,
                                                target_type=tt_api_impacts.OBJECT_TYPE.JOB_PERSON_POSITIVE,
                                                target_id=self.person_id,
                                                amount=1000),
                   game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.JOB,
                                                actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                actor_id=self.hero_id,
                                                target_type=tt_api_impacts.OBJECT_TYPE.JOB_PERSON_NEGATIVE,
                                                target_id=self.person_id,
                                                amount=2000),
                   game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.JOB,
                                                actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                actor_id=self.hero_id,
                                                target_type=tt_api_impacts.OBJECT_TYPE.JOB_PLACE_POSITIVE,
                                                target_id=self.place_id,
                                                amount=3000),
                   game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.JOB,
                                                actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                actor_id=self.hero_id,
                                                target_type=tt_api_impacts.OBJECT_TYPE.JOB_PLACE_NEGATIVE,
                                                target_id=self.place_id,
                                                amount=4000)]

        foreign_impacts = copy.deepcopy(impacts)
        for impact in foreign_impacts:
            impact.target_id += 1
            impact.amount = random.randint(1, 10000)

        logic.add_power_impacts(impacts)
        logic.add_power_impacts(foreign_impacts)

    def test_get_for_place(self):
        self.assertEqual(logic.get_job_power(place_id=self.place_id),
                         jobs_objects.JobPower(3000, 4000))

    def test_get_for_person(self):
        self.assertEqual(logic.get_job_power(person_id=self.person_id),
                         jobs_objects.JobPower(1000, 2000))

    def test_no_actor(self):
        self.assertRaises(NotImplementedError, logic.get_job_power)


class AddPowerImpactsTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_tt_services.debug_clear_service()

    def test_success(self):
        impacts = []

        for type in game_tt_services.IMPACT_TYPE.records:
            impacts.append(game_tt_services.PowerImpact.hero_2_person(type=type,
                                                                      hero_id=random.randint(1, 100),
                                                                      person_id=random.randint(1, 100),
                                                                      amount=random.randint(1, 100)))
            impacts.append(game_tt_services.PowerImpact.hero_2_place(type=type,
                                                                     hero_id=random.randint(1, 100),
                                                                     place_id=random.randint(1, 100),
                                                                     amount=random.randint(1, 100)))
        logic.add_power_impacts(impacts)

        loaded_impacts = []

        for api in [game_tt_services.personal_impacts, game_tt_services.crowd_impacts, game_tt_services.job_impacts]:
            loaded_impacts.extend(api.cmd_get_last_power_impacts(limit=100))

        for impact in loaded_impacts:
            impact.time = None

        self.assertCountEqual([impact for impact in impacts if not impact.type.is_FAME], loaded_impacts)

        fame_impacts = game_tt_services.fame_impacts.cmd_get_last_power_impacts(limit=100,
                                                                                actor_type=None,
                                                                                actor_id=None,
                                                                                target_type=None,
                                                                                target_id=None)

        for impact in fame_impacts:
            impact.time = None

        self.assertCountEqual([impact for impact in impacts if impact.type.is_FAME], fame_impacts)


class GetLastPowerImpactsTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_tt_services.debug_clear_service()

        self.impacts = []

        for type in game_tt_services.IMPACT_TYPE.records:
            self.impacts.append(game_tt_services.PowerImpact.hero_2_person(type=type,
                                                                           hero_id=random.randint(1, 100),
                                                                           person_id=random.randint(1, 100),
                                                                           amount=random.randint(1, 100)))
            self.impacts.append(game_tt_services.PowerImpact.hero_2_place(type=type,
                                                                          hero_id=random.randint(1, 100),
                                                                          place_id=random.randint(1, 100),
                                                                          amount=random.randint(1, 100)))

        with mock.patch('the_tale.game.turn.number', lambda: random.randint(1, 10000)):
            for impact in self.impacts:
                logic.add_power_impacts([impact])

    def test_success(self):

        loaded_impacts = logic.get_last_power_impacts(100)

        for impact in loaded_impacts:
            impact.time = None

        self.assertCountEqual([impact for impact in self.impacts if not impact.type.is_JOB and not impact.type.is_FAME],
                              loaded_impacts)

    def test_limit(self):
        loaded_impacts = logic.get_last_power_impacts(3)

        for impact in loaded_impacts:
            impact.time = None

        self.impacts.sort(key=lambda impact: (impact.turn, impact.time), reverse=True)

        self.assertEqual([impact for impact in self.impacts if not impact.type.is_JOB and not impact.type.is_FAME][:3],
                         loaded_impacts)
