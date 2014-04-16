# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.accounts.payments.goods import ResetHeroPreference
from the_tale.accounts.payments.price_list import PURCHASES_BY_UID

from the_tale.game.heroes import relations


class PriceListTests(testcase.TestCase):

    def setUp(self):
        super(PriceListTests, self).setUp()


    def test_all_preferences_in_prices(self):
        self.assertEqual(set(price.preference_type for price in PURCHASES_BY_UID.itervalues() if isinstance(price, ResetHeroPreference)),
                         set(relations.PREFERENCE_TYPE.records))
