# coding: utf-8

from common.utils import testcase

from game.logic import create_test_map

from game.bundles import BundlePrototype

from accounts.logic import register_user

from game.heroes.prototypes import HeroPrototype
from game.heroes.models import Hero
from game.models import Bundle
from game.prototypes import TimePrototype
from game.logic_storage import LogicStorage


class BundleTest(testcase.TestCase):

    def setUp(self):
        super(BundleTest, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.bundle = BundlePrototype.get_by_id(bundle_id)
        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)


    def test_remove(self):

        current_time = TimePrototype.get_current_time()

        for i in xrange(100):
            self.storage.process_turn()
            current_time.increment_turn()

        self.storage._test_save()

        # reload to simulate clean working
        bundle = BundlePrototype.get_by_id(self.bundle.id)

        bundle.remove()

        self.assertEqual(Hero.objects.all().count(), 1)

        self.assertEqual(Bundle.objects.all().count(), 0)
