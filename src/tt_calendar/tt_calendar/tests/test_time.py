
import unittest

from .. import time


class TimeTests(unittest.TestCase):

    def test_hour_restrictions(self):
        with self.assertRaises(ValueError):
            time.Time(hour='a')

        with self.assertRaises(ValueError):
            time.Time(hour=-1)

        with self.assertRaises(ValueError):
            time.Time(hour=24)

    def test_minute_restrictions(self):
        with self.assertRaises(ValueError):
            time.Time(minute='a')

        with self.assertRaises(ValueError):
            time.Time(minute=-1)

        with self.assertRaises(ValueError):
            time.Time(minute=60)

    def test_second_restrictions(self):
        with self.assertRaises(ValueError):
            time.Time(second='a')

        with self.assertRaises(ValueError):
            time.Time(second=-1)

        with self.assertRaises(ValueError):
            time.Time(second=60)

    def test_initialize__default(self):
        test_time = time.Time()

        self.assertEqual(test_time.hour, 0)
        self.assertEqual(test_time.minute, 0)
        self.assertEqual(test_time.second, 0)

    def test_initialize(self):
        test_time = time.Time(hour=1, minute=2, second=3)

        self.assertEqual(test_time.hour, 1)
        self.assertEqual(test_time.minute, 2)
        self.assertEqual(test_time.second, 3)

    def test_total_seconds(self):
        self.assertEqual(time.Time().total_seconds(), 0)
        self.assertEqual(time.Time(hour=1, minute=2, second=3).total_seconds(), 3723)

    def test_verbose(self):
        test_time = time.Time(hour=1, minute=2, second=3)

        self.assertEqual(test_time.verbose(), '01:02')
        self.assertEqual(test_time.verbose('{hour:0>2}:{minute:0>2}:{second:0>2}'), '01:02:03')
