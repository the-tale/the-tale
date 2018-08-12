import uuid
import datetime

from unittest import mock

from aiohttp import test_utils

from tt_web import postgresql as db

from .. import objects
from .. import operations
from .. import exceptions
from .. import relations

from . import helpers


class LogTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_create(self):
        item_id = uuid.uuid4()

        await operations.log(db.sql,
                             operation_type=relations.OPERATION_TYPE.PLACE_SELL_LOT,
                             lot_type=relations.LOT_TYPE.SELL,
                             item_type='xxx',
                             item_id=item_id,
                             owner_id=666,
                             price=100500,
                             data={'a': 'b'})

        result = await db.sql('SELECT * FROM log_records')

        self.assertEqual(result[0]['operation_type'], relations.OPERATION_TYPE.PLACE_SELL_LOT.value)
        self.assertEqual(result[0]['lot_type'], relations.LOT_TYPE.SELL.value)
        self.assertEqual(result[0]['item_type'], 'xxx')
        self.assertEqual(result[0]['item'], item_id)
        self.assertEqual(result[0]['owner'], 666)
        self.assertEqual(result[0]['price'], 100500)
        self.assertEqual(result[0]['data'], {'a': 'b'})


class PlaceSellLotsTests(helpers.BaseTests):

    async def check_new_lot(self, lot):
        result = await db.sql('SELECT * FROM log_records')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['operation_type'], relations.OPERATION_TYPE.PLACE_SELL_LOT.value)
        self.assertEqual(result[0]['lot_type'], lot.type.value)
        self.assertEqual(result[0]['item_type'], lot.item_type)
        self.assertEqual(result[0]['item'], lot.item_id)
        self.assertEqual(result[0]['owner'], lot.owner_id)
        self.assertEqual(result[0]['price'], lot.price)
        self.assertEqual(result[0]['data'], {})

        result = await db.sql('SELECT * FROM sell_lots')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['item_type'], lot.item_type)
        self.assertEqual(result[0]['item'], lot.item_id)
        self.assertEqual(result[0]['price'], lot.price)
        self.assertEqual(result[0]['owner'], lot.owner_id)


    @test_utils.unittest_run_loop
    async def test_success(self):
        lot = helpers.create_sell_lot()

        result = await db.sql('SELECT * FROM sell_lots')
        self.assertFalse(result)

        result = await db.sql('SELECT * FROM log_records')
        self.assertFalse(result)

        with mock.patch.object(operations.MarketInfoCache, 'soft_reset') as soft_reset:
            await operations.place_sell_lots([lot])

        self.assertTrue(soft_reset.called)

        await self.check_new_lot(lot)


    @test_utils.unittest_run_loop
    async def test_already_exists(self):
        lot = helpers.create_sell_lot()
        lot_2 = helpers.create_sell_lot(item_type=lot.item_type+'x',
                                        item_id=lot.item_id,
                                        owner_id=lot.owner_id+1,
                                        price=lot.price+1)

        result = await db.sql('SELECT * FROM sell_lots')
        self.assertFalse(result)

        result = await db.sql('SELECT * FROM log_records')
        self.assertFalse(result)

        await operations.place_sell_lots([lot])

        with self.assertRaises(exceptions.SellLotForItemAlreadyCreated):
            with mock.patch.object(operations.MarketInfoCache, 'soft_reset') as soft_reset:
                await operations.place_sell_lots([lot])

            self.assertFalse(soft_reset.called)

        await self.check_new_lot(lot)


class CloseSellLotTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_success(self):
        lot = helpers.create_sell_lot()
        lots_ids = await operations.place_sell_lots([lot])
        lot_id = lots_ids[0]

        with mock.patch.object(operations.MarketInfoCache, 'soft_reset') as soft_reset:
            lots = await operations.close_sell_lot(item_type=lot.item_type,
                                                   buyer_id=lot.owner_id+1,
                                                   price=lot.price,
                                                   number=100)
        for lot in lots:
            lot.created_at = None

        self.assertEqual(lots, [lot])
        self.assertTrue(soft_reset.called)

        result = await db.sql('SELECT * FROM sell_lots')
        self.assertFalse(result)

        result = await db.sql('SELECT * FROM log_records ORDER BY created_at DESC')
        self.assertEqual(len(result), 2)

        self.assertEqual(result[0]['operation_type'], relations.OPERATION_TYPE.CLOSE_SELL_LOT.value)
        self.assertEqual(result[0]['lot_type'], lot.type.value)
        self.assertEqual(result[0]['item_type'], lot.item_type)
        self.assertEqual(result[0]['item'], lot.item_id)
        self.assertEqual(result[0]['owner'], lot.owner_id)
        self.assertEqual(result[0]['price'], lot.price)
        self.assertEqual(result[0]['data'], {'buyer_id': lot.owner_id+1})


    @test_utils.unittest_run_loop
    async def test_success__multiple(self):
        lot_1 = helpers.create_sell_lot()
        lot_2 = helpers.create_sell_lot(price=lot_1.price+1)
        lot_3 = helpers.create_sell_lot()

        lots_ids = await operations.place_sell_lots([lot_1, lot_2, lot_3])

        with mock.patch.object(operations.MarketInfoCache, 'soft_reset') as soft_reset:
            lots = await operations.close_sell_lot(item_type=lot_1.item_type,
                                                   buyer_id=lot_1.owner_id+1,
                                                   price=lot_1.price,
                                                   number=100)

        for lot in lots:
            lot.created_at = None

        self.assertCountEqual(lots, [lot_1, lot_3])
        self.assertTrue(soft_reset.called)

        result = await db.sql('SELECT * FROM sell_lots')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['item'], lots_ids[1])

        result = await db.sql('SELECT * FROM log_records ORDER BY created_at DESC')
        self.assertEqual(len(result), 5)

        self.assertEqual(result[0]['operation_type'], relations.OPERATION_TYPE.CLOSE_SELL_LOT.value)
        self.assertEqual(result[1]['operation_type'], relations.OPERATION_TYPE.CLOSE_SELL_LOT.value)


    @test_utils.unittest_run_loop
    async def test_success__filter(self):
        lots = [helpers.create_sell_lot(item_type='type-1', price=1),
                helpers.create_sell_lot(item_type='type-1', price=2),
                helpers.create_sell_lot(item_type='type-1', price=3),
                helpers.create_sell_lot(item_type='type-2', price=1),
                helpers.create_sell_lot(item_type='type-2', price=2),
                helpers.create_sell_lot(item_type='type-2', price=3),
                helpers.create_sell_lot(item_type='type-3', price=1),
                helpers.create_sell_lot(item_type='type-3', price=2),
                helpers.create_sell_lot(item_type='type-3', price=3)]

        lots_ids = await operations.place_sell_lots(lots)

        result_lots = await operations.close_sell_lot(item_type='type-2',
                                                      buyer_id=78578,
                                                      price=2,
                                                      number=100)

        for lot in result_lots:
            lot.created_at = None

        self.assertCountEqual(result_lots, [lots[4]])


    @test_utils.unittest_run_loop
    async def test_success__owners_distribution(self):
        lot_1 = helpers.create_sell_lot(item_type='type-1', price=1, owner_id=100)
        lot_2 = helpers.create_sell_lot(item_type='type-1', price=1, owner_id=200)
        lots_3 = [helpers.create_sell_lot(item_type='type-1', price=1, owner_id=300)
                  for i in range(1000)]

        lots_ids = await operations.place_sell_lots([lot_1]+lots_3+[lot_2])

        owners = set()

        for i in range(20):
            result_lots = await operations.close_sell_lot(item_type='type-1',
                                                          buyer_id=78578,
                                                          price=1,
                                                          number=1)
            owners.add(result_lots[0].owner_id)

        self.assertEqual(owners, {100, 200, 300})


    @test_utils.unittest_run_loop
    async def test_success__number(self):
        lots = [helpers.create_sell_lot(item_type='type-1', price=1),
                helpers.create_sell_lot(item_type='type-1', price=1),
                helpers.create_sell_lot(item_type='type-1', price=1)]

        lots_ids = await operations.place_sell_lots(lots)

        items_ids = await operations.close_sell_lot(item_type='type-1',
                                                    buyer_id=78578,
                                                    price=1,
                                                    number=2)

        self.assertEqual(len(items_ids), 2)


    @test_utils.unittest_run_loop
    async def test_no_lot(self):
        with mock.patch.object(operations.MarketInfoCache, 'soft_reset') as soft_reset:
            items_ids = await operations.close_sell_lot(item_type='some type',
                                                        buyer_id=777,
                                                        price=23123,
                                                        number=100)

        self.assertEqual(items_ids, [])
        self.assertFalse(soft_reset.called)

        result = await db.sql('SELECT * FROM sell_lots')
        self.assertFalse(result)

        result = await db.sql('SELECT * FROM log_records')
        self.assertFalse(result)


class CancelSellLotTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_success(self):
        lot = helpers.create_sell_lot()
        lots_ids = await operations.place_sell_lots([lot])
        lot_id = lots_ids[0]

        with mock.patch.object(operations.MarketInfoCache, 'soft_reset') as soft_reset:
            lots = await operations.cancel_sell_lot(item_type=lot.item_type,
                                                    owner_id=lot.owner_id,
                                                    price=lot.price,
                                                    number=100)
        for lot in lots:
            lot.created_at = None

        self.assertEqual(lots, [lot])
        self.assertTrue(soft_reset.called)

        result = await db.sql('SELECT * FROM sell_lots')
        self.assertFalse(result)

        result = await db.sql('SELECT * FROM log_records ORDER BY created_at DESC')
        self.assertEqual(len(result), 2)

        self.assertEqual(result[0]['operation_type'], relations.OPERATION_TYPE.CANCEL_SELL_LOT.value)
        self.assertEqual(result[0]['lot_type'], lot.type.value)
        self.assertEqual(result[0]['item_type'], lot.item_type)
        self.assertEqual(result[0]['item'], lot.item_id)
        self.assertEqual(result[0]['owner'], lot.owner_id)
        self.assertEqual(result[0]['price'], lot.price)
        self.assertEqual(result[0]['data'], {})


    @test_utils.unittest_run_loop
    async def test_success__multiple(self):
        lot_1 = helpers.create_sell_lot()
        lot_2 = helpers.create_sell_lot(price=lot_1.price+1)
        lot_3 = helpers.create_sell_lot()

        lots_ids = await operations.place_sell_lots([lot_1, lot_2, lot_3])

        with mock.patch.object(operations.MarketInfoCache, 'soft_reset') as soft_reset:
            lots = await operations.cancel_sell_lot(item_type=lot_1.item_type,
                                                    owner_id=lot_1.owner_id,
                                                    price=lot_1.price,
                                                    number=100)

        for lot in lots:
            lot.created_at = None

        self.assertCountEqual(lots, [lot_1, lot_3])
        self.assertTrue(soft_reset.called)

        result = await db.sql('SELECT * FROM sell_lots')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['item'], lots_ids[1])

        result = await db.sql('SELECT * FROM log_records ORDER BY created_at DESC')
        self.assertEqual(len(result), 5)

        self.assertEqual(result[0]['operation_type'], relations.OPERATION_TYPE.CANCEL_SELL_LOT.value)
        self.assertEqual(result[1]['operation_type'], relations.OPERATION_TYPE.CANCEL_SELL_LOT.value)


    @test_utils.unittest_run_loop
    async def test_success__filter(self):
        lots = [helpers.create_sell_lot(item_type='type-1', price=1),
                helpers.create_sell_lot(item_type='type-1', price=2),
                helpers.create_sell_lot(item_type='type-1', price=3),
                helpers.create_sell_lot(item_type='type-2', price=1),
                helpers.create_sell_lot(item_type='type-2', price=2),
                helpers.create_sell_lot(item_type='type-2', price=3),
                helpers.create_sell_lot(item_type='type-3', price=1),
                helpers.create_sell_lot(item_type='type-3', price=2),
                helpers.create_sell_lot(item_type='type-3', price=3)]

        lots_ids = await operations.place_sell_lots(lots)

        result_lots = await operations.cancel_sell_lot(item_type='type-2',
                                                       owner_id=lots[4].owner_id,
                                                       price=2,
                                                       number=100)

        for lot in result_lots:
            lot.created_at = None

        self.assertCountEqual(result_lots, [lots[4]])


    @test_utils.unittest_run_loop
    async def test_success__filter_by_owner(self):
        lots = [helpers.create_sell_lot(item_type='type-1', price=1),
                helpers.create_sell_lot(item_type='type-1', price=2),
                helpers.create_sell_lot(item_type='type-1', price=3),
                helpers.create_sell_lot(item_type='type-2', price=1),
                helpers.create_sell_lot(item_type='type-2', price=2, owner_id=666),
                helpers.create_sell_lot(item_type='type-2', price=2, owner_id=777),
                helpers.create_sell_lot(item_type='type-3', price=1),
                helpers.create_sell_lot(item_type='type-3', price=2),
                helpers.create_sell_lot(item_type='type-3', price=3)]

        lots_ids = await operations.place_sell_lots(lots)

        result_lots = await operations.cancel_sell_lot(item_type='type-2',
                                                       owner_id=777,
                                                       price=2,
                                                       number=100)

        for lot in result_lots:
            lot.created_at = None

        self.assertCountEqual(result_lots, [lots[5]])


    @test_utils.unittest_run_loop
    async def test_success__number(self):
        lots = [helpers.create_sell_lot(item_type='type-1', price=1),
                helpers.create_sell_lot(item_type='type-1', price=1),
                helpers.create_sell_lot(item_type='type-1', price=1)]

        lots_ids = await operations.place_sell_lots(lots)

        items_ids = await operations.cancel_sell_lot(item_type='type-1',
                                                     owner_id=lots[0].owner_id,
                                                     price=1,
                                                     number=2)

        self.assertEqual(len(items_ids), 2)


    @test_utils.unittest_run_loop
    async def test_no_lot(self):
        with mock.patch.object(operations.MarketInfoCache, 'soft_reset') as soft_reset:
            items_ids = await operations.cancel_sell_lot(item_type='some type',
                                                         owner_id=777,
                                                         price=23123,
                                                         number=100)

        self.assertEqual(items_ids, [])
        self.assertFalse(soft_reset.called)

        result = await db.sql('SELECT * FROM sell_lots')
        self.assertFalse(result)

        result = await db.sql('SELECT * FROM log_records')
        self.assertFalse(result)


class LoadSellLotsTests(helpers.BaseTests):

    async def prepair_data(self):
        lots = [helpers.create_sell_lot(item_type='test.1', price=1, owner_id=1),
                helpers.create_sell_lot(item_type='test.1', price=1, owner_id=2),
                helpers.create_sell_lot(item_type='test.1', price=3, owner_id=3),
                helpers.create_sell_lot(item_type='test.1', price=4, owner_id=4),
                helpers.create_sell_lot(item_type='test.2', price=3, owner_id=1),
                helpers.create_sell_lot(item_type='test.3', price=4, owner_id=2),
                helpers.create_sell_lot(item_type='test.3', price=4, owner_id=3)]
        await operations.place_sell_lots(lots)
        return lots

    @test_utils.unittest_run_loop
    async def test_no_lots(self):
        await self.prepair_data()
        lots = await operations.load_sell_lots(owner_id=666)
        self.assertFalse(lots)


    @test_utils.unittest_run_loop
    async def test_has_info(self):
        existed_lots = await self.prepair_data()
        lots = await operations.load_sell_lots(owner_id=3)

        for lot in lots:
            lot.created_at = None

        self.assertCountEqual(lots, [existed_lots[2], existed_lots[6]])


class LoadMarketInfoTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_info(self):
        info = await operations._load_market_info()
        self.assertFalse(info)


    @test_utils.unittest_run_loop
    async def test_has_info(self):
        lots = [helpers.create_sell_lot(item_type='test.1', price=1),
                helpers.create_sell_lot(item_type='test.1', price=1),
                helpers.create_sell_lot(item_type='test.1', price=3),
                helpers.create_sell_lot(item_type='test.1', price=4),
                helpers.create_sell_lot(item_type='test.2', price=3),
                helpers.create_sell_lot(item_type='test.3', price=4),
                helpers.create_sell_lot(item_type='test.3', price=4)]

        await operations.place_sell_lots(lots)

        info = await operations._load_market_info()

        info.sort(key=lambda x: x.item_type)

        self.assertEqual(info, [objects.ItemTypeSummary(item_type='test.1', sell_number=4, min_sell_price=1, max_sell_price=4, owner_sell_number=0),
                                objects.ItemTypeSummary(item_type='test.2', sell_number=1, min_sell_price=3, max_sell_price=3, owner_sell_number=0),
                                objects.ItemTypeSummary(item_type='test.3', sell_number=2, min_sell_price=4, max_sell_price=4, owner_sell_number=0)])



class GetTypePricesTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_prices(self):
        info = await operations.get_type_prices('some-type')
        self.assertFalse(info)


    @test_utils.unittest_run_loop
    async def test_has_prices(self):
        lots = [helpers.create_sell_lot(item_type='test.1', price=1),
                helpers.create_sell_lot(item_type='test.1', price=1),
                helpers.create_sell_lot(item_type='test.1', price=3),
                helpers.create_sell_lot(item_type='test.1', price=4),
                helpers.create_sell_lot(item_type='test.2', price=3),
                helpers.create_sell_lot(item_type='test.3', price=4),
                helpers.create_sell_lot(item_type='test.3', price=4)]

        await operations.place_sell_lots(lots)

        prices = await operations.get_type_prices('test.1')

        self.assertEqual(prices, {1: 2, 3: 1, 4: 1})


class GetTypePricesForOwnerTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_prices(self):
        info = await operations.get_type_prices_for_owner('some-type', owner_id=666)
        self.assertFalse(info)


    @test_utils.unittest_run_loop
    async def test_has_prices(self):
        lots = [helpers.create_sell_lot(item_type='test.1', price=1, owner_id=777),
                helpers.create_sell_lot(item_type='test.1', price=1, owner_id=777),
                helpers.create_sell_lot(item_type='test.1', price=3),
                helpers.create_sell_lot(item_type='test.1', price=4, owner_id=777),
                helpers.create_sell_lot(item_type='test.2', price=3, owner_id=777),
                helpers.create_sell_lot(item_type='test.3', price=4),
                helpers.create_sell_lot(item_type='test.3', price=4)]

        await operations.place_sell_lots(lots)

        prices = await operations.get_type_prices_for_owner('test.1', owner_id=777)

        self.assertEqual(prices, {1: 2, 4: 1})


class GetOwnerItemsNumberTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_items(self):
        info = await operations.get_owner_items_number(owner_id=666)
        self.assertFalse(info)


    @test_utils.unittest_run_loop
    async def test_has_prices(self):
        lots = [helpers.create_sell_lot(item_type='test.1', price=1),
                helpers.create_sell_lot(item_type='test.1', price=1),
                helpers.create_sell_lot(item_type='test.1', price=3),
                helpers.create_sell_lot(item_type='test.1', price=4, owner_id=777),
                helpers.create_sell_lot(item_type='test.2', price=3, owner_id=777),
                helpers.create_sell_lot(item_type='test.3', price=4),
                helpers.create_sell_lot(item_type='test.3', price=4)]

        await operations.place_sell_lots(lots)

        info = await operations.get_owner_items_number(owner_id=666)

        self.assertEqual(info, {'test.1': 3, 'test.3': 2})


class LoadHistoryPageTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_records(self):
        info = await operations.load_history_page(page=1, records_on_page=10)
        self.assertFalse(info)

    @test_utils.unittest_run_loop
    async def test_first_page(self):
        await helpers.prepair_history_log()

        info = await operations.load_history_page(page=1, records_on_page=3)

        self.assertEqual([(record.item_type, record.price) for record in info],
                         [('test.3', 4), ('test.2', 3), ('test.3', 4)])

    @test_utils.unittest_run_loop
    async def test_second_page(self):
        await helpers.prepair_history_log()

        info = await operations.load_history_page(page=2, records_on_page=3)

        self.assertEqual([(record.item_type, record.price) for record in info],
                         [('test.1', 1), ('test.1', 1)])


class HistoryRecordsNumberTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_records(self):
        number = await operations.history_records_number()
        self.assertEqual(number, 0)

    @test_utils.unittest_run_loop
    async def test_first_page(self):
        await helpers.prepair_history_log()

        number = await operations.history_records_number()
        self.assertEqual(number, 5)


class StatisticsTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_records(self):
        statistics = await operations.statistics(time_from=datetime.datetime.fromtimestamp(0),
                                                 time_till=datetime.datetime.utcnow()+datetime.timedelta(days=1))
        self.assertEqual(statistics, {'sell_lots_placed': 0,
                                      'sell_lots_closed': 0,
                                      'turnover': 0})


    @test_utils.unittest_run_loop
    async def test_has_records(self):
        await helpers.prepair_history_log()

        statistics = await operations.statistics(time_from=datetime.datetime.fromtimestamp(0),
                                                 time_till=datetime.datetime.utcnow()+datetime.timedelta(days=1))
        self.assertEqual(statistics, {'sell_lots_placed': 7,
                                      'sell_lots_closed': 5,
                                      'turnover': 13})


    @test_utils.unittest_run_loop
    async def test_time_interval(self):
        await helpers.prepair_history_log()

        result = await db.sql('SELECT created_at FROM log_records ORDER BY created_at ASC')

        time_from = result[3]['created_at']
        time_till = result[-2]['created_at']

        statistics = await operations.statistics(time_from=time_from,
                                                 time_till=time_till)
        self.assertEqual(statistics, {'sell_lots_placed': 5,
                                      'sell_lots_closed': 3,
                                      'turnover': 8})
