# coding: utf-8

import datetime

from collections import Counter

from common.utils import testcase

from common.utils.logic import random_value_by_priority, verbose_timedelta, get_or_create
from common.utils.decorators import lazy_property

_get_or_create_state = None # for get_or_create tests

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

    def test_lazy_property_decorator(self):

        class X(object):

            def __init__(self):
                self.count = 0

            @lazy_property
            def test(self):
                self.count += 1
                return self.count

        x = X()

        self.assertEqual(x.count, 0)
        x.test
        x.test
        self.assertEqual(x.count, 1)
        x.test
        self.assertEqual(x.count, 1)


    def test_get_or_create__by_get(self):
        def get(x, y): return x + y

        self.assertEqual(get_or_create(get_method=get, create_method=None, exception=None, kwargs={'x': 222, 'y': 444}), 666)


    def test_get_or_create__by_create(self):
        def get(x, y): return None
        def create(x, y): return x + y

        self.assertEqual(get_or_create(get_method=get, create_method=create, exception=None, kwargs={'x': 222, 'y': 444}), 666)


    def test_get_or_create__by_second_get(self):
        global _get_or_create_state
        _get_or_create_state = 'first'

        def get(x, y):
            global _get_or_create_state
            if _get_or_create_state == 'first':
                _get_or_create_state = 'second'
                return None
            return x + y

        def create(x, y): raise Exception

        self.assertEqual(get_or_create(get_method=get, create_method=create, exception=Exception, kwargs={'x': 222, 'y': 444}), 666)
