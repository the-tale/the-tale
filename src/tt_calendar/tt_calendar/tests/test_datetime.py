
import unittest

from .. import time
from .. import date
from .. import datetime


class DateTimeTests(unittest.TestCase):

    def test_constuct(self):
        test_datetime = datetime.DateTime(year=1, month=2, day=3, hour=4, minute=5, second=6)

        self.assertEqual(test_datetime.date, date.Date(year=1, month=2, day=3))
        self.assertEqual(test_datetime.time, time.Time(hour=4, minute=5, second=6))

    def test_attributes_access(self):
        test_datetime = datetime.DateTime(year=1, month=2, day=3, hour=4, minute=5, second=6)

        self.assertEqual(test_datetime.year, 1)
        self.assertEqual(test_datetime.month, 2)
        self.assertEqual(test_datetime.day, 3)
        self.assertEqual(test_datetime.hour, 4)
        self.assertEqual(test_datetime.minute, 5)
        self.assertEqual(test_datetime.second, 6)

    def test_replace(self):
        test_datetime = datetime.DateTime(year=1, month=2, day=3, hour=4, minute=5, second=6)

        self.assertEqual(test_datetime.replace(year=10), datetime.DateTime(year=10, month=2, day=3, hour=4, minute=5, second=6))
        self.assertEqual(test_datetime.replace(month=3), datetime.DateTime(year=1, month=3, day=3, hour=4, minute=5, second=6))
        self.assertEqual(test_datetime.replace(day=10), datetime.DateTime(year=1, month=2, day=10, hour=4, minute=5, second=6))
        self.assertEqual(test_datetime.replace(hour=10), datetime.DateTime(year=1, month=2, day=3, hour=10, minute=5, second=6))
        self.assertEqual(test_datetime.replace(minute=10), datetime.DateTime(year=1, month=2, day=3, hour=4, minute=10, second=6))
        self.assertEqual(test_datetime.replace(second=10), datetime.DateTime(year=1, month=2, day=3, hour=4, minute=5, second=10))

    def test_total_seconds(self):
        self.assertEqual(datetime.DateTime().total_seconds(), 0)
        self.assertEqual(datetime.DateTime(year=1, month=2, day=3, hour=4, minute=5, second=6).total_seconds(), 46929906)

    def test_verbose_full(self):
        test_datetime = datetime.DateTime(year=1, month=2, day=3, hour=4, minute=5, second=6)
        self.assertEqual(test_datetime.verbose_full(), '4 юного квинта сырого месяца 2 года 04:05')

    def test_verbose_short(self):
        test_datetime = datetime.DateTime(year=1, month=2, day=3, hour=4, minute=5, second=6)
        self.assertEqual(test_datetime.verbose_short(), '4.3.2 04:05')
