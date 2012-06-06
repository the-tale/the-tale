# coding: utf-8

from django.test import TestCase

from game.models import Time
from game.prototypes import TimePrototype


class TimeTest(TestCase):

    def test_creation(self):
        self.assertEqual(Time.objects.all().count(), 0)
        time = TimePrototype.create()
        self.assertEqual(time.turn_number, 0)
        self.assertEqual(Time.objects.all().count(), 1)
        time = TimePrototype.create()
        self.assertEqual(time.turn_number, 0)
        self.assertEqual(Time.objects.all().count(), 2)
        time = TimePrototype.create()
        self.assertEqual(time.turn_number, 0)
        self.assertEqual(Time.objects.all().count(), 3)

    def test_get_current_time(self):
        self.assertEqual(Time.objects.all().count(), 0)
        time = TimePrototype.get_current_time()
        self.assertEqual(time.turn_number, 0)
        self.assertEqual(Time.objects.all().count(), 1)
        time = TimePrototype.get_current_time()
        self.assertEqual(time.turn_number, 0)
        self.assertEqual(Time.objects.all().count(), 1)

    def test_increment_turn(self):
        self.assertEqual(Time.objects.all().count(), 0)
        time = TimePrototype.get_current_time()
        self.assertEqual(time.turn_number, 0)

        time.increment_turn()
        self.assertEqual(time.turn_number, 1)
        time.save()

        time = TimePrototype.get_current_time()
        self.assertEqual(time.turn_number, 1)

    def test_ui_info(self):
        time = TimePrototype.get_current_time()
        time.increment_turn()

        self.assertEqual(time.ui_info(), { 'number': 1 })
