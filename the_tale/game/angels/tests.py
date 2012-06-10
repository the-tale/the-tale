# coding: utf-8

from django.test import TestCase

from game.logic import create_test_bundle, create_test_map, test_bundle_save

from game.balance import constants as c

from game.angels.prototypes import AngelPrototype

from game.angels.models import Angel
from game.heroes.models import Hero
from game.quests.models import Quest
from game.actions.models import Action
from game.models import Bundle, BundleMember

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
        test_bundle_save(self, self.bundle)

    def test_energy_regeneration(self):
        new_enegry = 1
        self.angel.set_energy_at_turn(666, new_enegry)

        self.assertEqual(self.angel.updated_at_turn, 666)

        self.assertTrue(self.angel.updated)
        self.assertEqual(self.angel.get_energy_at_turn(self.angel.updated_at_turn), new_enegry)

        self.assertEqual(self.angel.get_energy_at_turn(self.angel.updated_at_turn + 1), new_enegry)
        self.assertEqual(self.angel.get_energy_at_turn(self.angel.updated_at_turn + c.ANGEL_ENERGY_REGENERATION_PERIOD), new_enegry + c.ANGEL_ENERGY_REGENERATION_AMAUNT)

        self.assertEqual(self.angel.get_energy_at_turn(self.angel.updated_at_turn + 9999999999), self.angel.energy_maximum)
        test_bundle_save(self, self.bundle)

    def test_remove(self):
        turn_number = 1

        for i in xrange(100):
            self.bundle.process_turn(turn_number)
            turn_number += 1

        test_bundle_save(self, self.bundle)

        # reload to simulate clean working without bundles and etc.
        angel = AngelPrototype.get_by_id(self.angel.id)

        angel.remove()

        self.assertEqual(Angel.objects.all().count(), 0)
        self.assertEqual(Hero.objects.all().count(), 0)
        self.assertEqual(Quest.objects.all().count(), 0)
        self.assertEqual(Action.objects.all().count(), 0)

        self.assertEqual(BundleMember.objects.all().count(), 0)

        # bundles should not be removed by that method, see AccountPrototype.remove
        self.assertEqual(Bundle.objects.all().count(), 1)
