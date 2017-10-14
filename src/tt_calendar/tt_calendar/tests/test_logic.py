
import random
import unittest
import datetime

from .. import date
from .. import time
from .. import logic
from .. import relations


class ActualRealFeastsTests(unittest.TestCase):

    def test_no_feasts(self):
        now = datetime.datetime(year=34, month=2, day=28, hour=0, minute=0, second=0)
        self.assertEqual(list(logic.actual_real_feasts(now)), [])

    def test_has_feast(self):
        for feast in relations.REAL_FEAST.records:
            for interval in feast.intervals:
                self.assertEqual(list(logic.actual_real_feasts(interval[0] + (interval[1]-interval[0])/2)), [feast])


class ActualDatesTests(unittest.TestCase):

    def test_no_dates(self):
        now = date.Date(month=0, day=5)
        self.assertEqual(list(logic.actual_dates(now, relations.DATE)), [])

    def test_has_dates(self):
        for check_date in relations.DATE.records:
            for interval in check_date.intervals:
                now = date.Date(month=int(interval[0][0] + (interval[1][0]-interval[0][0])/2),
                                day=int(interval[0][1] + (interval[1][1]-interval[0][1])/2))
                self.assertEqual(list(logic.actual_dates(now, relations.DATE)), [check_date])


class IsDayOfTests(unittest.TestCase):

    def test_day_off(self):
        self.assertTrue(logic.is_day_off(date.Date(day=random.choice((14, 29, 44, 59, 74, 89)))))

    def test_new_year(self):
        self.assertTrue(logic.is_day_off(date.Date(day=1)))

    def test_weekday(self):
        self.assertFalse(logic.is_day_off(date.Date(day=2)))
        self.assertFalse(logic.is_day_off(date.Date(month=3, day=2)))


class DayTmesTests(unittest.TestCase):

    def test_day_times(self):
        self.assertEqual(list(logic.day_times(time.Time(hour=0))), [relations.DAY_TIME.DARK_TIME, relations.DAY_TIME.NIGHT])
        self.assertEqual(list(logic.day_times(time.Time(hour=1))), [relations.DAY_TIME.DARK_TIME, relations.DAY_TIME.NIGHT])
        self.assertEqual(list(logic.day_times(time.Time(hour=2))), [relations.DAY_TIME.DARK_TIME, relations.DAY_TIME.NIGHT])
        self.assertEqual(list(logic.day_times(time.Time(hour=3))), [relations.DAY_TIME.DARK_TIME, relations.DAY_TIME.NIGHT])
        self.assertEqual(list(logic.day_times(time.Time(hour=4))), [relations.DAY_TIME.DARK_TIME, relations.DAY_TIME.NIGHT])
        self.assertEqual(list(logic.day_times(time.Time(hour=5))), [relations.DAY_TIME.DARK_TIME, relations.DAY_TIME.NIGHT])
        self.assertEqual(list(logic.day_times(time.Time(hour=6))), [relations.DAY_TIME.DARK_TIME, relations.DAY_TIME.NIGHT])
        self.assertEqual(list(logic.day_times(time.Time(hour=7))), [relations.DAY_TIME.LIGHT_TIME, relations.DAY_TIME.MORNING, relations.DAY_TIME.DAWN])
        self.assertEqual(list(logic.day_times(time.Time(hour=8))), [relations.DAY_TIME.LIGHT_TIME, relations.DAY_TIME.MORNING])
        self.assertEqual(list(logic.day_times(time.Time(hour=9))), [relations.DAY_TIME.LIGHT_TIME, relations.DAY_TIME.MORNING])
        self.assertEqual(list(logic.day_times(time.Time(hour=10))), [relations.DAY_TIME.LIGHT_TIME, relations.DAY_TIME.DAY])
        self.assertEqual(list(logic.day_times(time.Time(hour=11))), [relations.DAY_TIME.LIGHT_TIME, relations.DAY_TIME.DAY])
        self.assertEqual(list(logic.day_times(time.Time(hour=12))), [relations.DAY_TIME.LIGHT_TIME, relations.DAY_TIME.DAY])
        self.assertEqual(list(logic.day_times(time.Time(hour=13))), [relations.DAY_TIME.LIGHT_TIME, relations.DAY_TIME.DAY])
        self.assertEqual(list(logic.day_times(time.Time(hour=14))), [relations.DAY_TIME.LIGHT_TIME, relations.DAY_TIME.DAY])
        self.assertEqual(list(logic.day_times(time.Time(hour=15))), [relations.DAY_TIME.LIGHT_TIME, relations.DAY_TIME.DAY])
        self.assertEqual(list(logic.day_times(time.Time(hour=16))), [relations.DAY_TIME.LIGHT_TIME, relations.DAY_TIME.EVENING])
        self.assertEqual(list(logic.day_times(time.Time(hour=17))), [relations.DAY_TIME.LIGHT_TIME, relations.DAY_TIME.EVENING])
        self.assertEqual(list(logic.day_times(time.Time(hour=18))), [relations.DAY_TIME.LIGHT_TIME, relations.DAY_TIME.EVENING])
        self.assertEqual(list(logic.day_times(time.Time(hour=19))), [relations.DAY_TIME.DARK_TIME, relations.DAY_TIME.NIGHT, relations.DAY_TIME.SUNSET])
        self.assertEqual(list(logic.day_times(time.Time(hour=20))), [relations.DAY_TIME.DARK_TIME, relations.DAY_TIME.NIGHT])
        self.assertEqual(list(logic.day_times(time.Time(hour=21))), [relations.DAY_TIME.DARK_TIME, relations.DAY_TIME.NIGHT])
        self.assertEqual(list(logic.day_times(time.Time(hour=22))), [relations.DAY_TIME.DARK_TIME, relations.DAY_TIME.NIGHT])
        self.assertEqual(list(logic.day_times(time.Time(hour=23))), [relations.DAY_TIME.DARK_TIME, relations.DAY_TIME.NIGHT])
