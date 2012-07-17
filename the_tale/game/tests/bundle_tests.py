# coding: utf-8

from django.test import TestCase

from game.logic import create_test_bundle, create_test_map, test_bundle_save

from game.bundles import BundlePrototype

from game.angels.models import Angel
from game.heroes.models import Hero
from game.actions.models import Action
from game.models import Bundle, BundleMember
from game.prototypes import TimePrototype

class BundleTest(TestCase):

    def setUp(self):
        create_test_map()

        self.bundle = create_test_bundle('AngelTest')
        self.angel = self.bundle.tests_get_angel()
        self.hero = self.bundle.tests_get_hero()


    def test_remove(self):

        current_time = TimePrototype.get_current_time()

        for i in xrange(100):
            self.bundle.process_turn()
            current_time.increment_turn()

        test_bundle_save(self, self.bundle)

        # reload to simulate clean working
        bundle = BundlePrototype.get_by_id(self.bundle.id)

        bundle.remove()

        self.assertEqual(Angel.objects.all().count(), 1)
        self.assertEqual(Hero.objects.all().count(), 1)
        self.assertTrue(Action.objects.all().count() > 0)

        self.assertEqual(BundleMember.objects.all().count(), 0)
        self.assertEqual(Bundle.objects.all().count(), 0)
