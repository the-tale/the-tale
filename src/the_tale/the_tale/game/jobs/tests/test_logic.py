
import smart_imports

smart_imports.all()


class FakeJob(objects.Job):
    ACTOR = 'place'

    ACTOR_TYPE = tt_api_impacts.OBJECT_TYPE.PLACE
    POSITIVE_TARGET_TYPE = tt_api_impacts.OBJECT_TYPE.JOB_PLACE_POSITIVE
    NEGATIVE_TARGET_TYPE = tt_api_impacts.OBJECT_TYPE.JOB_PLACE_NEGATIVE
    NORMAL_POWER = 1000

    def load_power(self, actor_id):
        return politic_power_logic.get_job_power(place_id=actor_id)

    def load_inner_circle(self, actor_id):
        return politic_power_logic.get_inner_circle(place_id=actor_id)

    def get_job_power(self, actor_id):
        return 1.13

    def get_project_name(self, actor_id):
        return 'Project name'

    def get_objects(self, actor_id):
        return {'person': None,
                'place': places_storage.places[actor_id]}

    def get_effects_priorities(self, actor_id):
        return {effect: 1 for effect in effects.EFFECT.records}


class JobPowerTests(utils_testcase.TestCase):

    def test_job_power__one(self):
        delta = (c.JOB_MAX_POWER - c.JOB_MIN_POWER) / 2
        self.assertEqual(logic.job_power(1, [1]), c.JOB_MIN_POWER + delta)

    def test_job_power__two(self):
        delta = (c.JOB_MAX_POWER - c.JOB_MIN_POWER) / 3
        self.assertEqual(logic.job_power(1, [1, 2]), c.JOB_MIN_POWER + delta)
        self.assertEqual(logic.job_power(2, [1, 2]), c.JOB_MIN_POWER + delta * 2)

    def test_job_power__many(self):
        delta = (c.JOB_MAX_POWER - c.JOB_MIN_POWER) / 4
        self.assertEqual(logic.job_power(1, [1, 2, 3]), c.JOB_MIN_POWER + delta)
        self.assertEqual(logic.job_power(2, [1, 2, 3]), c.JOB_MIN_POWER + delta * 2)
        self.assertEqual(logic.job_power(3, [1, 2, 3]), c.JOB_MIN_POWER + delta * 3)

    def test_job_power__equal(self):
        delta = (c.JOB_MAX_POWER - c.JOB_MIN_POWER) / 4
        self.assertEqual(logic.job_power(1, [1, 2, 2]), c.JOB_MIN_POWER + delta)
        self.assertEqual(logic.job_power(2, [1, 2, 2]), c.JOB_MIN_POWER + delta * 2)


class CreateJobTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

    @mock.patch('the_tale.game.turn.number', lambda: 777)
    def test_new_job(self):
        job = logic.create_job(FakeJob)

        self.assertEqual(job.created_at_turn, 777)
        self.assertEqual(job.power_required, 1000 * job.effect.power_modifier)


class UpdateJobTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.job = logic.create_job(FakeJob)

        game_tt_services.debug_clear_service()

    def give_power(self, impacts):
        impacts_to_apply = []

        for hero_id, impact in impacts:
            if impact > 0:
                impacts_to_apply.append(game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.JOB,
                                                                     actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                                     actor_id=hero_id,
                                                                     target_type=self.job.POSITIVE_TARGET_TYPE,
                                                                     target_id=self.place_1.id,
                                                                     amount=impact))
            else:
                impacts_to_apply.append(game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.JOB,
                                                                     actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                                     actor_id=hero_id,
                                                                     target_type=self.job.NEGATIVE_TARGET_TYPE,
                                                                     target_id=self.place_1.id,
                                                                     amount=-impact))

        politic_power_logic.add_power_impacts(impacts_to_apply)

    def test_job_is_incomplete(self):
        original_job = copy.deepcopy(self.job)

        operations = logic.update_job(self.job, self.place_1.id)

        self.assertEqual(original_job, self.job)
        self.assertEqual(operations, ())

    def test_exclude_previouse_effect(self):
        for i in range(10):
            old_effect = self.job.effect

            self.give_power([(666, self.job.power_required)])

            logic.update_job(self.job, self.place_1.id)

            self.assertNotEqual(self.job.effect, old_effect)

    def test_reset_positive_power(self):
        self.give_power([(666, self.job.power_required),
                         (777, -self.job.power_required + 1)])

        power = politic_power_logic.get_job_power(place_id=self.place_1.id)

        self.assertEqual(power, objects.JobPower(positive=self.job.power_required,
                                                 negative=self.job.power_required - 1))

        old_power_required = self.job.power_required

        logic.update_job(self.job, self.place_1.id)

        power = politic_power_logic.get_job_power(place_id=self.place_1.id)

        self.assertEqual(power, objects.JobPower(positive=0,
                                                 negative=old_power_required - 1))

    def test_reset_negative_power(self):
        self.give_power([(666, self.job.power_required - 1),
                         (777, -self.job.power_required)])

        power = politic_power_logic.get_job_power(place_id=self.place_1.id)

        self.assertEqual(power, objects.JobPower(positive=self.job.power_required - 1,
                                                 negative=self.job.power_required))

        old_power_required = self.job.power_required

        logic.update_job(self.job, self.place_1.id)

        power = politic_power_logic.get_job_power(place_id=self.place_1.id)

        self.assertEqual(power, objects.JobPower(positive=old_power_required - 1,
                                                 negative=0))

    def test_apply_effects(self):
        hero_id = self.accounts_factory.create_account().id

        politic_power_logic.add_power_impacts([game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                                            actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                                            actor_id=hero_id,
                                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                                            target_id=self.place_1.id,
                                                                            amount=1)])

        self.give_power([(hero_id, self.job.power_required)])

        operations = logic.update_job(self.job, self.place_1.id)

        self.assertTrue(operations)

        for operation in operations:
            operation()
