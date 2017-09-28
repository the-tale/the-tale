
import uuid
import datetime
import collections

from unittest import mock

from the_tale.common.utils import testcase

from the_tale.game.logic import create_test_map
from the_tale.game.logic_storage import LogicStorage

from .. import tt_api
from .. import objects


class TTAPiTests(testcase.TestCase):

    def setUp(self):
        super().setUp()
        create_test_map()
        tt_api.debug_clear_service()

        self.lots = [objects.Lot(owner_id=666, full_type='#item-type-1', item_id=uuid.uuid4(), price=100500),
                     objects.Lot(owner_id=777, full_type='#item-type-1', item_id=uuid.uuid4(), price=17),
                     objects.Lot(owner_id=666, full_type='#item-type-2', item_id=uuid.uuid4(), price=500)]


    def tearDown(self):
        super().tearDown()
        tt_api.debug_clear_service()


    def test_place_sell_lot(self):

        tt_api.place_sell_lots([self.lots[0]])

        data = tt_api.info()

        self.assertEqual(data, [objects.ItemTypeSummary(full_type='#item-type-1',
                                                        sell_number=1,
                                                        min_sell_price=100500,
                                                        max_sell_price=100500)])


    def test_info(self):
        tt_api.place_sell_lots(self.lots)

        data = tt_api.info()

        data.sort(key=lambda x: x.full_type)

        self.assertEqual(data, [objects.ItemTypeSummary(full_type='#item-type-1',
                                                        sell_number=2,
                                                        min_sell_price=17,
                                                        max_sell_price=100500),
                                objects.ItemTypeSummary(full_type='#item-type-2',
                                                        sell_number=1,
                                                        min_sell_price=500,
                                                        max_sell_price=500)])


    def test_item_type_prices(self):
        tt_api.place_sell_lots(self.lots)

        prices, owner_prices = tt_api.item_type_prices(item_type='#item-type-1',
                                                       owner_id=0)

        self.assertEqual(prices, {100500: 1, 17: 1})
        self.assertEqual(owner_prices, {})


    def test_item_type_prices__with_owner(self):
        tt_api.place_sell_lots(self.lots)

        prices, owner_prices = tt_api.item_type_prices(item_type='#item-type-1',
                                                       owner_id=666)

        self.assertEqual(prices, {100500: 1, 17: 1})
        self.assertEqual(owner_prices, {100500: 1})



    def test_close_lot(self):
        tt_api.place_sell_lots([self.lots[0]])

        lots = tt_api.close_lot(item_type=self.lots[0].full_type,
                                price=self.lots[0].price,
                                buyer_id=123)

        self.assertEqual(lots[0], self.lots[0])


    def test_close_lot__no_lot(self):
        tt_api.place_sell_lots([self.lots[0]])

        lots = tt_api.close_lot(item_type=self.lots[0].full_type,
                                price=self.lots[0].price+1,
                                buyer_id=123)

        self.assertEqual(lots, [])


    def test_cancel_lot(self):
        tt_api.place_sell_lots([self.lots[0]])

        lots = tt_api.cancel_lot(item_type=self.lots[0].full_type,
                                 price=self.lots[0].price,
                                 owner_id=self.lots[0].owner_id)

        self.assertEqual(lots[0], self.lots[0])


    def test_cancel_lot__no_lot_with_price(self):
        tt_api.place_sell_lots([self.lots[0]])

        lots = tt_api.cancel_lot(item_type=self.lots[0].full_type,
                                 price=self.lots[0].price+1,
                                 owner_id=self.lots[0].owner_id)

        self.assertEqual(lots, [])


    def test_cancel_lot__no_lot_with_owner(self):
        tt_api.place_sell_lots([self.lots[0]])

        lots = tt_api.cancel_lot(item_type=self.lots[0].full_type,
                                 price=self.lots[0].price,
                                 owner_id=self.lots[0].owner_id+1)

        self.assertEqual(lots, [])



    def test_list_sell_lots__no_lots(self):
        tt_api.place_sell_lots(self.lots)

        lots = tt_api.list_sell_lots(owner_id=79877)
        self.assertEqual(lots, [])


    def test_list_sell_lots__has_lots(self):
        tt_api.place_sell_lots(self.lots)

        lots = tt_api.list_sell_lots(owner_id=666)

        for lot in lots:
            lot.created_at = None

        self.assertCountEqual(lots, [self.lots[0], self.lots[2]])


    def test_history__no_records(self):
        page, total_records, records = tt_api.history(page=1, records_on_page=2)

        self.assertEqual(page, 1)
        self.assertEqual(total_records, 0)
        self.assertEqual(records, [])


    def test_history__has_records(self):
        tt_api.place_sell_lots(self.lots)

        lots = tt_api.close_lot(item_type=self.lots[0].full_type,
                                price=self.lots[0].price,
                                buyer_id=123)

        lots = tt_api.close_lot(item_type=self.lots[2].full_type,
                                price=self.lots[2].price,
                                buyer_id=123)

        lots = tt_api.close_lot(item_type=self.lots[1].full_type,
                                price=self.lots[1].price,
                                buyer_id=123)

        page, total_records, records = tt_api.history(page=1, records_on_page=2)

        self.assertEqual(page, 1)
        self.assertEqual(total_records, 3)
        self.assertEqual([(record.item_type, record.price) for record in records],
                         [('#item-type-1', 17),
                          ('#item-type-2', 500)])


    def test_statistics__no_records(self):
        statistics = tt_api.statistics(time_from=datetime.datetime.fromtimestamp(0),
                                       time_till=datetime.datetime.utcnow()+datetime.timedelta(days=1))

        self.assertEqual(statistics, {'sell_lots_closed': 0,
                                      'sell_lots_placed': 0,
                                      'turnover': 0})


    def test_statistics__has_records(self):
        tt_api.place_sell_lots(self.lots)

        lots = tt_api.close_lot(item_type=self.lots[0].full_type,
                                price=self.lots[0].price,
                                buyer_id=123)

        lots = tt_api.close_lot(item_type=self.lots[2].full_type,
                                price=self.lots[2].price,
                                buyer_id=123)

        lots = tt_api.close_lot(item_type=self.lots[1].full_type,
                                price=self.lots[1].price,
                                buyer_id=123)

        statistics = tt_api.statistics(time_from=datetime.datetime.fromtimestamp(0),
                                       time_till=datetime.datetime.utcnow()+datetime.timedelta(days=1))

        self.assertEqual(statistics,  {'sell_lots_closed': 3,
                                       'sell_lots_placed': 3,
                                       'turnover': 101017})
