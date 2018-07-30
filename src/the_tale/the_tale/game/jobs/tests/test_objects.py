
import smart_imports

smart_imports.all()


class FakeJob(objects.Job):
    ACTOR = 'place'

    ACTOR_TYPE = tt_api_impacts.OBJECT_TYPE.PLACE
    POSITIVE_TARGET_TYPE = tt_api_impacts.OBJECT_TYPE.JOB_PLACE_POSITIVE
    NEGATIVE_TARGET_TYPE = tt_api_impacts.OBJECT_TYPE.JOB_PLACE_NEGATIVE
    NORMAL_POWER = 1000


class JobTest(utils_testcase.TestCase):

    @mock.patch('the_tale.game.turn.number', lambda: 666)
    def setUp(self):
        super(JobTest, self).setUp()
        linguistics_logic.sync_static_restrictions()
        self.job = logic.create_job(FakeJob)

    def test_create(self):
        self.assertEqual(self.job.created_at_turn, 666)
        self.assertEqual(self.job.power_required, 1000 * self.job.effect.power_modifier)
        self.assertTrue(self.job.effect.group.is_ON_HEROES)

    def test_serialization(self):
        self.assertEqual(self.job.serialize(), FakeJob.deserialize(self.job.serialize()).serialize())

    def test_is_completed(self):
        delta = self.job.power_required / 2

        self.assertFalse(self.job.is_completed(objects.JobPower(positive=delta, negative=delta)))
        self.assertTrue(self.job.is_completed(objects.JobPower(positive=delta * 3, negative=delta)))
        self.assertTrue(self.job.is_completed(objects.JobPower(positive=delta, negative=delta * 3)))
        self.assertTrue(self.job.is_completed(objects.JobPower(positive=delta * 3, negative=delta * 3)))

    def test_get_apply_effect_method(self):
        delta = self.job.power_required / 2

        self.assertEqual(self.job.get_apply_effect_method(objects.JobPower(positive=delta, negative=delta)),
                         self.job.effect.logic.apply_negative)

        self.assertEqual(self.job.get_apply_effect_method(objects.JobPower(positive=delta * 3, negative=delta)),
                         self.job.effect.logic.apply_positive)

        self.assertEqual(self.job.get_apply_effect_method(objects.JobPower(positive=delta, negative=delta * 3)),
                         self.job.effect.logic.apply_negative)

        self.assertEqual(self.job.get_apply_effect_method(objects.JobPower(positive=delta * 3, negative=delta * 3)),
                         self.job.effect.logic.apply_negative)
