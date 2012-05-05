# coding: utf-8

from django.test import TestCase

from game.logic import create_test_bundle, create_test_map

from game.balance import constants as c

class AngelTest(TestCase):

    def setUp(self):
        create_test_map()

        self.bundle = create_test_bundle('AngelTest')
        self.angel = self.bundle.tests_get_angel()
        self.hero = self.bundle.tests_get_hero()

    def tearDown(self):
        pass


    def test_create(self):
        self.assertTrue(not self.angel.updated)
        self.assertEqual(self.angel.updated_at_turn, 0)
        self.assertEqual(self.angel.get_energy_at_turn(1), c.ANGEL_ENERGY_MAX)


    def test_energy_regeneration(self):
        new_enegry = 1
        self.angel.set_energy_at_turn(666, new_enegry)

        self.assertEqual(self.angel.updated_at_turn, 666)

        self.assertTrue(self.angel.updated)
        self.assertEqual(self.angel.get_energy_at_turn(self.angel.updated_at_turn), new_enegry)

        self.assertEqual(self.angel.get_energy_at_turn(self.angel.updated_at_turn + 1), new_enegry)
        self.assertEqual(self.angel.get_energy_at_turn(self.angel.updated_at_turn + c.ANGEL_ENERGY_REGENERATION_PERIOD), new_enegry + c.ANGEL_ENERGY_REGENERATION_AMAUNT)

        self.assertEqual(self.angel.get_energy_at_turn(self.angel.updated_at_turn + 9999999999), self.angel.energy_maximum)
