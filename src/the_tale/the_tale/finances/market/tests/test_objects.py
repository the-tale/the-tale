# coding: utf-8

import datetime

from the_tale.common.utils import testcase

from the_tale.game.logic import create_test_map

from the_tale.finances.market import conf
from the_tale.finances.market import logic
from the_tale.finances.market import goods_types



class LotTests(testcase.TestCase):


    def setUp(self):
        super(LotTests, self).setUp()

        create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.good_1 = goods_types.test_hero_good.create_good('good-1')

        self.price_1 = 666

        self.lot_1 = logic.reserve_lot(self.account_1.id, self.good_1, price=self.price_1)


    def test_time_to_end(self):
        self.assertTrue(self.lot_1.time_to_end > datetime.timedelta(days=conf.settings.LOT_LIVE_TIME-1))

        self.lot_1.created_at = datetime.datetime.now() - datetime.timedelta(days=conf.settings.LOT_LIVE_TIME+1)

        self.assertEqual(self.lot_1.time_to_end, datetime.timedelta(days=0))
