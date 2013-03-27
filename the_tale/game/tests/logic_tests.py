# coding: utf-8

from common.utils import testcase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.bundles import BundlePrototype
from game.models import Bundle
from game.logic import remove_game_data, create_test_map

from game.heroes.models import Hero


class LogicTests(testcase.TestCase):

    def setUp(self):
        super(LogicTests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.account_id = account_id
        self.bundle = BundlePrototype.get_by_id(bundle_id)

    def test_remove_game_data(self):

        self.assertEqual(Bundle.objects.all().count(), 1)
        self.assertEqual(Hero.objects.all().count(), 1)

        remove_game_data(AccountPrototype.get_by_id(self.account_id))

        self.assertEqual(Bundle.objects.all().count(), 0)
        self.assertEqual(Hero.objects.all().count(), 0)
