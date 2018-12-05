
import datetime

from tt_web import handlers
from tt_web import exceptions as tt_exceptions

from tt_web.common import pagination

from tt_protocol.protocol import market_pb2

from . import protobuf
from . import exceptions
from . import operations


@handlers.api(market_pb2.PlaceSellLotRequest)
async def place_sell_lot(message, **kwargs):
    try:
        lots_ids = await operations.place_sell_lots(lots=[protobuf.to_sell_lot(lot) for lot in message.lots])
    except exceptions.SellLotForItemAlreadyCreated as e:
        raise tt_exceptions.ApiError(code='market.apply.sell_lot_for_item_already_created', message=str(e))

    return market_pb2.PlaceSellLotResponse(lots_ids=[lot_id.hex for lot_id in lots_ids])


@handlers.api(market_pb2.CloseSellLotRequest)
async def close_sell_lot(message, **kwargs):
    lots = await operations.close_sell_lot(item_type=message.item_type,
                                           buyer_id=message.buyer_id,
                                           price=message.price,
                                           number=message.number)
    return market_pb2.CloseSellLotResponse(lots=[protobuf.from_sell_lot(lot) for lot in lots])


@handlers.api(market_pb2.CancelSellLotRequest)
async def cancel_sell_lot(message, **kwargs):
    lots = await operations.cancel_sell_lot(item_type=message.item_type,
                                            owner_id=message.owner_id,
                                            price=message.price,
                                            number=message.number)
    return market_pb2.CancelSellLotResponse(lots=[protobuf.from_sell_lot(lot) for lot in lots])


@handlers.api(market_pb2.CancelSellLotsByTypeRequest)
async def cancel_sell_lots_by_type(message, **kwargs):
    lots = await operations.cancel_sell_lots_by_type(item_type=message.item_type)
    return market_pb2.CancelSellLotsByTypeResponse(lots=[protobuf.from_sell_lot(lot) for lot in lots])


@handlers.api(market_pb2.ListSellLotsRequest)
async def list_sell_lots(message, **kwargs):
    lots = await operations.load_sell_lots(owner_id=message.owner_id)
    return market_pb2.ListSellLotsResponse(lots=[protobuf.from_sell_lot_info(lot) for lot in lots])


@handlers.api(market_pb2.InfoRequest)
async def info(message, **kwargs):
    info = await operations.MARKET_INFO_CACHE.get_value()

    if message.HasField('owner_id'):
        owner_items_number = await operations.get_owner_items_number(message.owner_id)
        for summary in info:
            summary.owner_sell_number = owner_items_number.get(summary.item_type, 0)

    return market_pb2.InfoResponse(info=[protobuf.from_item_type_summary(summary) for summary in info])


@handlers.api(market_pb2.ItemTypePricesRequest)
async def item_type_prices(message, **kwargs):
    prices = await operations.get_type_prices(message.item_type)
    owner_prices = None

    if message.HasField('owner_id'):
        owner_prices = await operations.get_type_prices_for_owner(item_type=message.item_type,
                                                                  owner_id=message.owner_id)

    return market_pb2.ItemTypePricesResponse(prices=prices,
                                             owner_prices=owner_prices)


@handlers.api(market_pb2.HistoryRequest)
async def history(message, **kwargs):

    records_number = await operations.history_records_number()

    page = pagination.normalize_page(page=message.page,
                                     records_number=records_number,
                                     records_on_page=message.records_on_page)

    records = await operations.load_history_page(page=page,
                                                 records_on_page=message.records_on_page)

    return market_pb2.HistoryResponse(records=[protobuf.from_history_record(record) for record in records],
                                      total_records=records_number,
                                      page=page)


@handlers.api(market_pb2.StatisticsRequest)
async def statistics(message, **kwargs):

    statistics = await operations.statistics(time_from=datetime.datetime.fromtimestamp(message.time_from),
                                             time_till=datetime.datetime.fromtimestamp(message.time_till))

    return market_pb2.StatisticsResponse(sell_lots_placed=statistics['sell_lots_placed'],
                                         sell_lots_closed=statistics['sell_lots_closed'],
                                         turnover=statistics['turnover'])


@handlers.api(market_pb2.DebugClearServiceRequest)
async def debug_clear_service(message, **kwargs):
    await operations.clean_database()
    return market_pb2.DebugClearServiceResponse()
