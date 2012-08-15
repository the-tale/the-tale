# coding: utf-8

from collections import Counter

from django.test import TestCase

from common.utils.logic import random_value_by_priority

class LogicTest(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass


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
