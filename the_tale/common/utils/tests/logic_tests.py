# coding: utf-8
import datetime

from collections import Counter

from common.utils import testcase

from common.utils.logic import random_value_by_priority, verbose_timedelta

class LogicTest(testcase.TestCase):

    def setUp(self):
        super(LogicTest, self).setUp()

    def test_random_value_by_priority(self):
        counter = Counter()

        choices = [('0', 0),
                   ('a', 1),
                   ('b', 10),
                   ('c', 100)]

        counter.update([random_value_by_priority(choices) for i in xrange(10000)])

        self.assertTrue(counter['0'] == 0)
        self.assertTrue(counter['a'])
        self.assertTrue(counter['b'])
        self.assertTrue(counter['c'])

        self.assertTrue(counter['0'] < counter['a'] < counter['b'] < counter['c'])

    def test_verbose_timedelta(self):
        self.assertEqual(u'1 день', verbose_timedelta(datetime.timedelta(days=1)))
        self.assertEqual(u'101 день', verbose_timedelta(datetime.timedelta(days=101)))
        self.assertEqual(u'2 дня', verbose_timedelta(datetime.timedelta(days=2)))
        self.assertEqual(u'33 дня', verbose_timedelta(datetime.timedelta(days=33)))
        self.assertEqual(u'4 дня', verbose_timedelta(datetime.timedelta(days=4)))
        self.assertEqual(u'5 дней', verbose_timedelta(datetime.timedelta(days=5)))
        self.assertEqual(u'5 дней', verbose_timedelta(datetime.timedelta(seconds=5*24*60*60)))

        self.assertEqual(u'1 час', verbose_timedelta(datetime.timedelta(seconds=60*60)))
        self.assertEqual(u'2 часа', verbose_timedelta(datetime.timedelta(seconds=2*60*60)))
        self.assertEqual(u'23 часа', verbose_timedelta(datetime.timedelta(seconds=23*60*60)))
        self.assertEqual(u'4 часа', verbose_timedelta(datetime.timedelta(seconds=4*60*60)))
        self.assertEqual(u'5 часов', verbose_timedelta(datetime.timedelta(seconds=5*60*60)))

        self.assertEqual(u'1 минута', verbose_timedelta(datetime.timedelta(seconds=60)))
        self.assertEqual(u'2 минуты', verbose_timedelta(datetime.timedelta(seconds=2*60)))
        self.assertEqual(u'23 минуты', verbose_timedelta(datetime.timedelta(seconds=23*60)))
        self.assertEqual(u'4 минуты', verbose_timedelta(datetime.timedelta(seconds=4*60)))
        self.assertEqual(u'5 минут', verbose_timedelta(datetime.timedelta(seconds=5*60)))

        self.assertEqual(u'меньше минуты', verbose_timedelta(datetime.timedelta(seconds=49)))
