# coding: utf-8
from the_tale.common.utils import testcase

from the_tale.game.logic import create_test_map
from the_tale.game.logic_storage import LogicStorage

from the_tale.game.companions import logic as companions_logic

from the_tale.game.companions.tests import helpers


class CommonTests(testcase.TestCase):

    def setUp(self):
        super(CommonTests, self).setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]


    def test_rarities_abilities(self):
        for rarity, rarity_abilities in helpers.RARITIES_ABILITIES.iteritems():
            companion = companions_logic.create_random_companion_record('%s companion' % rarity,
                                                                        abilities=rarity_abilities)
            self.assertEqual(companion.rarity, rarity)
