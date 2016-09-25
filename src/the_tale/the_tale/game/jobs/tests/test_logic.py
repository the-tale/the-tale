# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.game.balance import constants as c

from the_tale.game.jobs import logic



class LogicTests(testcase.TestCase):

    def setUp(self):
        super(LogicTests, self).setUp()


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
