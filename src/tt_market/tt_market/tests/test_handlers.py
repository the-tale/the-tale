
import uuid
import time

from aiohttp import test_utils

from tt_protocol.protocol import market_pb2

from tt_web import postgresql as db

from .. import objects
from .. import protobuf
from .. import relations
from .. import operations

from . import helpers


class PlaceSellLotTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_success(self):
        lot = helpers.create_sell_lot()

        request = await self.client.post('/place-sell-lot', data=market_pb2.PlaceSellLotRequest(lots=[protobuf.from_sell_lot(lot)]).SerializeToString())
        await self.check_success(request, market_pb2.PlaceSellLotResponse)

        result = await db.sql('SELECT * FROM log_records')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['operation_type'], relations.OPERATION_TYPE.PLACE_SELL_LOT.value)
        self.assertEqual(result[0]['lot_type'], lot.type.value)
        self.assertEqual(result[0]['item_type'], lot.item_type)
        self.assertEqual(result[0]['item'], lot.item_id)
        self.assertEqual(result[0]['owner'], lot.owner_id)
        self.assertEqual(result[0]['price'], lot.price)
        self.assertEqual(result[0]['data'], {})

    @test_utils.unittest_run_loop
    async def test_already_created(self):
        lot = helpers.create_sell_lot()

        request = await self.client.post('/place-sell-lot', data=market_pb2.PlaceSellLotRequest(lots=[protobuf.from_sell_lot(lot)]).SerializeToString())
        await self.check_success(request, market_pb2.PlaceSellLotResponse)

        request = await self.client.post('/place-sell-lot', data=market_pb2.PlaceSellLotRequest(lots=[protobuf.from_sell_lot(lot)]).SerializeToString())
        await self.check_error(request, error='market.apply.sell_lot_for_item_already_created')

        result = await db.sql('SELECT * FROM log_records')

        self.assertEqual(len(result), 1)

    @test_utils.unittest_run_loop
    async def test_too_large_price(self):
        lot = helpers.create_sell_lot(price=2**63)

        request = await self.client.post('/place-sell-lot', data=market_pb2.PlaceSellLotRequest(lots=[protobuf.from_sell_lot(lot)]).SerializeToString())
        await self.check_error(request, error='market.apply.sell_lot_maximum_price_exceeded')

        result = await db.sql('SELECT * FROM log_records')

        self.assertEqual(len(result), 0)

    @test_utils.unittest_run_loop
    async def test_price_below_zero(self):
        lot = helpers.create_sell_lot(price=-1)

        # check that protobuf will rise error
        with self.assertRaises(ValueError):
            await self.client.post('/place-sell-lot', data=market_pb2.PlaceSellLotRequest(lots=[protobuf.from_sell_lot(lot)]).SerializeToString())

        result = await db.sql('SELECT * FROM log_records')

        self.assertEqual(len(result), 0)


class CloseSellLotTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_success(self):
        lot = helpers.create_sell_lot()
        request = await self.client.post('/place-sell-lot', data=market_pb2.PlaceSellLotRequest(lots=[protobuf.from_sell_lot(lot)]).SerializeToString())
        data = await self.check_success(request, market_pb2.PlaceSellLotResponse)

        request = await self.client.post('/close-sell-lot',
                                         data=market_pb2.CloseSellLotRequest(item_type=lot.item_type,
                                                                             buyer_id=lot.owner_id+1,
                                                                             price=lot.price,
                                                                             number=1).SerializeToString())
        data = await self.check_success(request, market_pb2.CloseSellLotResponse)
        self.assertEqual([protobuf.to_sell_lot(x) for x in data.lots], [lot])

        result = await db.sql('SELECT * FROM sell_lots')
        self.assertFalse(result)

        result = await db.sql('SELECT * FROM log_records')
        self.assertEqual(len(result), 2)

    @test_utils.unittest_run_loop
    async def test_no_lot_to_close(self):
        request = await self.client.post('/close-sell-lot', data=market_pb2.CloseSellLotRequest(item_type='wrong type',
                                                                                                buyer_id=777,
                                                                                                price=1,
                                                                                                number=1).SerializeToString())
        data = await self.check_success(request, market_pb2.CloseSellLotResponse)
        self.assertEqual(list(data.lots), [])

        result = await db.sql('SELECT * FROM sell_lots')
        self.assertFalse(result)

        result = await db.sql('SELECT * FROM log_records')
        self.assertEqual(len(result), 0)


class CancelSellLotTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_success(self):
        lot = helpers.create_sell_lot()
        request = await self.client.post('/place-sell-lot', data=market_pb2.PlaceSellLotRequest(lots=[protobuf.from_sell_lot(lot)]).SerializeToString())
        data = await self.check_success(request, market_pb2.PlaceSellLotResponse)

        request = await self.client.post('/cancel-sell-lot',
                                         data=market_pb2.CancelSellLotRequest(item_type=lot.item_type,
                                                                              owner_id=lot.owner_id,
                                                                              price=lot.price,
                                                                              number=1).SerializeToString())
        data = await self.check_success(request, market_pb2.CancelSellLotResponse)
        self.assertEqual([protobuf.to_sell_lot(x) for x in data.lots], [lot])

        result = await db.sql('SELECT * FROM sell_lots')
        self.assertFalse(result)

        result = await db.sql('SELECT * FROM log_records')
        self.assertEqual(len(result), 2)

    @test_utils.unittest_run_loop
    async def test_no_lot_to_cancel(self):
        request = await self.client.post('/cancel-sell-lot', data=market_pb2.CancelSellLotRequest(item_type='wrong type',
                                                                                                  owner_id=777,
                                                                                                  price=1,
                                                                                                  number=1).SerializeToString())
        data = await self.check_success(request, market_pb2.CancelSellLotResponse)
        self.assertEqual(list(data.lots), [])

        result = await db.sql('SELECT * FROM sell_lots')
        self.assertFalse(result)

        result = await db.sql('SELECT * FROM log_records')
        self.assertEqual(len(result), 0)


class CancelSellLotsByTypeTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_success(self):
        lot = helpers.create_sell_lot()
        request = await self.client.post('/place-sell-lot', data=market_pb2.PlaceSellLotRequest(lots=[protobuf.from_sell_lot(lot)]).SerializeToString())
        data = await self.check_success(request, market_pb2.PlaceSellLotResponse)

        request = await self.client.post('/cancel-sell-lots-by-type',
                                         data=market_pb2.CancelSellLotsByTypeRequest(item_type=lot.item_type).SerializeToString())

        data = await self.check_success(request, market_pb2.CancelSellLotsByTypeResponse)

        self.assertEqual([protobuf.to_sell_lot(x) for x in data.lots], [lot])

        result = await db.sql('SELECT * FROM sell_lots')
        self.assertFalse(result)

        result = await db.sql('SELECT * FROM log_records')
        self.assertEqual(len(result), 2)

    @test_utils.unittest_run_loop
    async def test_no_lot_to_cancel(self):
        request = await self.client.post('/cancel-sell-lots-by-type',
                                         data=market_pb2.CancelSellLotsByTypeRequest(item_type='wrong type').SerializeToString())

        data = await self.check_success(request, market_pb2.CancelSellLotsByTypeResponse)
        self.assertEqual(list(data.lots), [])

        result = await db.sql('SELECT * FROM sell_lots')
        self.assertFalse(result)

        result = await db.sql('SELECT * FROM log_records')
        self.assertEqual(len(result), 0)


class InfoTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_lots(self):
        request = await self.client.post('/info', data=market_pb2.InfoRequest().SerializeToString())
        data = await self.check_success(request, market_pb2.InfoResponse)
        self.assertFalse(data.info)

    @test_utils.unittest_run_loop
    async def test_has_lots(self):
        lots = [helpers.create_sell_lot(item_type='test.1', price=1),
                helpers.create_sell_lot(item_type='test.1', price=1),
                helpers.create_sell_lot(item_type='test.1', price=3),
                helpers.create_sell_lot(item_type='test.1', price=4),
                helpers.create_sell_lot(item_type='test.2', price=3),
                helpers.create_sell_lot(item_type='test.3', price=4),
                helpers.create_sell_lot(item_type='test.3', price=4)]

        await operations.place_sell_lots(lots)

        request = await self.client.post('/info', data=market_pb2.InfoRequest().SerializeToString())
        data = await self.check_success(request, market_pb2.InfoResponse)

        summaries = [objects.ItemTypeSummary(item_type='test.1', sell_number=4, min_sell_price=1, max_sell_price=4, owner_sell_number=0),
                     objects.ItemTypeSummary(item_type='test.2', sell_number=1, min_sell_price=3, max_sell_price=3, owner_sell_number=0),
                     objects.ItemTypeSummary(item_type='test.3', sell_number=2, min_sell_price=4, max_sell_price=4, owner_sell_number=0)]

        original_info = [protobuf.from_item_type_summary(summary) for summary in summaries]

        self.assertCountEqual(data.info, original_info)

    @test_utils.unittest_run_loop
    async def test_has_lots__with_owner(self):
        lots = [helpers.create_sell_lot(item_type='test.1', price=1),
                helpers.create_sell_lot(item_type='test.1', price=1),
                helpers.create_sell_lot(item_type='test.1', price=3),
                helpers.create_sell_lot(item_type='test.1', price=4, owner_id=777),
                helpers.create_sell_lot(item_type='test.2', price=3, owner_id=777),
                helpers.create_sell_lot(item_type='test.3', price=4),
                helpers.create_sell_lot(item_type='test.3', price=4)]

        await operations.place_sell_lots(lots)

        request = await self.client.post('/info', data=market_pb2.InfoRequest(owner_id=666).SerializeToString())
        data = await self.check_success(request, market_pb2.InfoResponse)

        summaries = [objects.ItemTypeSummary(item_type='test.1', sell_number=4, min_sell_price=1, max_sell_price=4, owner_sell_number=3),
                     objects.ItemTypeSummary(item_type='test.2', sell_number=1, min_sell_price=3, max_sell_price=3, owner_sell_number=0),
                     objects.ItemTypeSummary(item_type='test.3', sell_number=2, min_sell_price=4, max_sell_price=4, owner_sell_number=2)]

        original_info = [protobuf.from_item_type_summary(summary) for summary in summaries]

        self.assertCountEqual(data.info, original_info)



class ItemTypePricesTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_lots(self):
        request = await self.client.post('/item-type-prices', data=market_pb2.ItemTypePricesRequest(item_type='some.type').SerializeToString())
        data = await self.check_success(request, market_pb2.ItemTypePricesResponse)
        self.assertFalse(data.prices)
        self.assertFalse(data.owner_prices)

    @test_utils.unittest_run_loop
    async def test_has_lots(self):
        lots = [helpers.create_sell_lot(item_type='test.1', price=1),
                helpers.create_sell_lot(item_type='test.1', price=1),
                helpers.create_sell_lot(item_type='test.1', price=3),
                helpers.create_sell_lot(item_type='test.1', price=4),
                helpers.create_sell_lot(item_type='test.2', price=3),
                helpers.create_sell_lot(item_type='test.3', price=4),
                helpers.create_sell_lot(item_type='test.3', price=4)]

        await operations.place_sell_lots(lots)

        request = await self.client.post('/item-type-prices', data=market_pb2.ItemTypePricesRequest(item_type='test.1').SerializeToString())
        data = await self.check_success(request, market_pb2.ItemTypePricesResponse)

        self.assertEqual(data.prices, {1: 2, 3: 1, 4: 1})
        self.assertEqual(data.owner_prices, {})

    @test_utils.unittest_run_loop
    async def test_has_lots__owner_filter(self):
        lots = [helpers.create_sell_lot(item_type='test.1', price=1, owner_id=777),
                helpers.create_sell_lot(item_type='test.1', price=1, owner_id=777),
                helpers.create_sell_lot(item_type='test.1', price=3),
                helpers.create_sell_lot(item_type='test.1', price=4, owner_id=777),
                helpers.create_sell_lot(item_type='test.2', price=3, owner_id=777),
                helpers.create_sell_lot(item_type='test.3', price=4),
                helpers.create_sell_lot(item_type='test.3', price=4)]

        await operations.place_sell_lots(lots)

        request = await self.client.post('/item-type-prices', data=market_pb2.ItemTypePricesRequest(item_type='test.1', owner_id=777).SerializeToString())
        data = await self.check_success(request, market_pb2.ItemTypePricesResponse)

        self.assertEqual(data.prices, {1: 2, 3: 1, 4: 1})
        self.assertEqual(data.owner_prices, {1: 2, 4: 1})


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
        request = await self.client.post('/list-sell-lots', data=market_pb2.ListSellLotsRequest(owner_id=666).SerializeToString())
        data = await self.check_success(request, market_pb2.ListSellLotsResponse)
        self.assertFalse(data.lots)

    @test_utils.unittest_run_loop
    async def test_has_lots(self):
        lots = await self.prepair_data()

        request = await self.client.post('/list-sell-lots', data=market_pb2.ListSellLotsRequest(owner_id=3).SerializeToString())
        data = await self.check_success(request, market_pb2.ListSellLotsResponse)

        self.assertCountEqual([{'item_type': lot.item_type, 'price': lot.price, 'item_id': lot.item_id} for lot in data.lots],
                              [{'item_type': lots[2].item_type, 'price': lots[2].price, 'item_id': lots[2].item_id.hex},
                               {'item_type': lots[6].item_type, 'price': lots[6].price, 'item_id': lots[6].item_id.hex}])


class HistoryTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_records(self):
        request = await self.client.post('/history', data=market_pb2.HistoryRequest(page=1, records_on_page=3).SerializeToString())
        data = await self.check_success(request, market_pb2.HistoryResponse)

        self.assertEqual(list(data.records), [])
        self.assertEqual(data.total_records, 0)
        self.assertEqual(data.page, 1)

    @test_utils.unittest_run_loop
    async def test_first_page(self):
        await helpers.prepair_history_log()

        request = await self.client.post('/history', data=market_pb2.HistoryRequest(page=1, records_on_page=3).SerializeToString())
        data = await self.check_success(request, market_pb2.HistoryResponse)

        self.assertEqual([(record.item_type, record.price) for record in data.records],
                         [('test.3', 4), ('test.2', 3), ('test.3', 4)])
        self.assertEqual(data.total_records, 5)
        self.assertEqual(data.page, 1)

    @test_utils.unittest_run_loop
    async def test_second_page(self):
        await helpers.prepair_history_log()

        request = await self.client.post('/history', data=market_pb2.HistoryRequest(page=2, records_on_page=3).SerializeToString())
        data = await self.check_success(request, market_pb2.HistoryResponse)

        self.assertEqual([(record.item_type, record.price) for record in data.records],
                         [('test.1', 1), ('test.1', 1)])
        self.assertEqual(data.total_records, 5)
        self.assertEqual(data.page, 2)

    @test_utils.unittest_run_loop
    async def test_large_page(self):
        await helpers.prepair_history_log()

        request = await self.client.post('/history', data=market_pb2.HistoryRequest(page=20, records_on_page=3).SerializeToString())
        data = await self.check_success(request, market_pb2.HistoryResponse)

        self.assertEqual([(record.item_type, record.price) for record in data.records],
                         [('test.1', 1), ('test.1', 1)])
        self.assertEqual(data.total_records, 5)
        self.assertEqual(data.page, 2)

    @test_utils.unittest_run_loop
    async def test_small(self):
        await helpers.prepair_history_log()

        request = await self.client.post('/history', data=market_pb2.HistoryRequest(page=0, records_on_page=3).SerializeToString())
        data = await self.check_success(request, market_pb2.HistoryResponse)

        self.assertEqual([(record.item_type, record.price) for record in data.records],
                         [('test.3', 4), ('test.2', 3), ('test.3', 4)])
        self.assertEqual(data.total_records, 5)
        self.assertEqual(data.page, 1)


class StatisticsTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_records(self):
        request = await self.client.post('/statistics', data=market_pb2.StatisticsRequest(time_from=0,
                                                                                          time_till=time.time()+1).SerializeToString())
        data = await self.check_success(request, market_pb2.StatisticsResponse)

        self.assertEqual(data.sell_lots_placed, 0)
        self.assertEqual(data.sell_lots_closed, 0)
        self.assertEqual(data.turnover, '0')

    @test_utils.unittest_run_loop
    async def test_has_records(self):
        await helpers.prepair_history_log()

        request = await self.client.post('/statistics', data=market_pb2.StatisticsRequest(time_from=0,
                                                                                          time_till=time.time()+1).SerializeToString())
        data = await self.check_success(request, market_pb2.StatisticsResponse)

        self.assertEqual(data.sell_lots_placed, 7)
        self.assertEqual(data.sell_lots_closed, 5)
        self.assertEqual(data.turnover, '13')

    @test_utils.unittest_run_loop
    async def test_time_iterval(self):
        await helpers.prepair_history_log()

        result = await db.sql('SELECT created_at FROM log_records ORDER BY created_at ASC')

        time_from = result[3]['created_at']
        time_till = result[-2]['created_at']

        request = await self.client.post('/statistics',
                                         data=market_pb2.StatisticsRequest(time_from=time.mktime(time_from.timetuple())+
                                                                                     time_from.microsecond/10**6,
                                                                           time_till=time.mktime(time_till.timetuple())+
                                                                                     time_till.microsecond/10**6).SerializeToString())
        data = await self.check_success(request, market_pb2.StatisticsResponse)

        self.assertEqual(data.sell_lots_placed, 5)
        self.assertEqual(data.sell_lots_closed, 3)
        self.assertEqual(data.turnover, '8')


class DoesLotExistForItemTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_lot(self):
        request = await self.client.post('/does-lot-exist-for-item',
                                         data=market_pb2.DoesLotExistForItemRequest(item_type='xxx',
                                                                                    item_id=uuid.uuid4().hex).SerializeToString())
        data = await self.check_success(request, market_pb2.DoesLotExistForItemResponse)

        self.assertFalse(data.exists)

    @test_utils.unittest_run_loop
    async def test_no_lot_type(self):
        item_id = uuid.uuid4()

        lot = helpers.create_sell_lot(item_type='yyy', item_id=item_id)

        await operations.place_sell_lots([lot])

        request = await self.client.post('/does-lot-exist-for-item',
                                         data=market_pb2.DoesLotExistForItemRequest(item_type='xxx',
                                                                                    item_id=item_id.hex).SerializeToString())
        data = await self.check_success(request, market_pb2.DoesLotExistForItemResponse)

        self.assertFalse(data.exists)

    @test_utils.unittest_run_loop
    async def test_no_lot_id(self):
        lot = helpers.create_sell_lot(item_type='xxx')

        await operations.place_sell_lots([lot])

        exists = await operations.does_lot_exist_for_item(item_type='xxx', item_id=uuid.uuid4())
        self.assertFalse(exists)

        request = await self.client.post('/does-lot-exist-for-item',
                                         data=market_pb2.DoesLotExistForItemRequest(item_type='xxx',
                                                                                    item_id=uuid.uuid4().hex).SerializeToString())
        data = await self.check_success(request, market_pb2.DoesLotExistForItemResponse)

        self.assertFalse(data.exists)

    @test_utils.unittest_run_loop
    async def test_has_lot(self):
        item_id = uuid.uuid4()
        lot = helpers.create_sell_lot(item_type='xxx', item_id=item_id)

        await operations.place_sell_lots([lot])

        request = await self.client.post('/does-lot-exist-for-item',
                                         data=market_pb2.DoesLotExistForItemRequest(item_type='xxx',
                                                                                    item_id=item_id.hex).SerializeToString())
        data = await self.check_success(request, market_pb2.DoesLotExistForItemResponse)

        self.assertTrue(data.exists)
