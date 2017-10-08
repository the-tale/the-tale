
import unittest

from .. import date


class DateTests(unittest.TestCase):

    def test_year_restrictions(self):
        with self.assertRaises(ValueError):
            date.Date(year='a')

        with self.assertRaises(ValueError):
            date.Date(year=-1)

    def test_month_restrictions(self):
        with self.assertRaises(ValueError):
            date.Date(month='a')

        with self.assertRaises(ValueError):
            date.Date(month=-1)

        with self.assertRaises(ValueError):
            date.Date(month=12)

    def test_day_restrictions(self):
        with self.assertRaises(ValueError):
            date.Date(day='a')

        with self.assertRaises(ValueError):
            date.Date(day=-1)

        with self.assertRaises(ValueError):
            date.Date(day=90)

    def test_initialize__default(self):
        test_date = date.Date()

        self.assertEqual(test_date.year, 0)
        self.assertEqual(test_date.month, 0)
        self.assertEqual(test_date.day, 0)

    def test_initialize(self):
        test_date = date.Date(year=1, month=2, day=3)

        self.assertEqual(test_date.year, 1)
        self.assertEqual(test_date.month, 2)
        self.assertEqual(test_date.day, 3)

    def test_quint(self):
        self.assertEqual(date.Date(day=3).quint, 0)
        self.assertEqual(date.Date(day=33).quint, 2)
        self.assertEqual(date.Date(day=67).quint, 4)
        self.assertEqual(date.Date(day=89).quint, 5)

    def test_quint_day(self):
        self.assertEqual(date.Date(day=3).quint_day, 3)
        self.assertEqual(date.Date(day=33).quint_day, 3)
        self.assertEqual(date.Date(day=67).quint_day, 7)
        self.assertEqual(date.Date(day=89).quint_day, 14)

    def test_total_seconds(self):
        self.assertEqual(date.Date().total_seconds(), 0)
        self.assertEqual(date.Date(year=1, month=2, day=3).total_seconds(), 46915200)

    def test_verbose_full(self):
        self.assertEqual(date.Date(year=1, month=2, day=3).verbose_full(), '4 юного квинта сырого месяца 2 года')

    def test_verbose_short(self):
        self.assertEqual(date.Date(year=1, month=2, day=3).verbose_short(), '4.3.2')
