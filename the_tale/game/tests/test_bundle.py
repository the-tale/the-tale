# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.game.logic import create_test_map

from the_tale.game.bundles import BundlePrototype

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.heroes.models import Hero
from the_tale.game.models import Bundle
from the_tale.game.prototypes import TimePrototype
from the_tale.game.logic_storage import LogicStorage


class BundleTest(testcase.TestCase):

    def setUp(self):
        super(BundleTest, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.bundle = BundlePrototype.get_by_id(bundle_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]


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
