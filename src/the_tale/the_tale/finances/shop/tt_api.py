
import uuid
import time
import datetime

from django.conf import settings as project_settings

from dext.common.utils.urls import url
from dext.common.utils import s11n

from tt_protocol.protocol import market_pb2

from the_tale.common.utils import tt_api

from . import conf
from . import objects


def place_sell_lots(lots):

    raw_lots = []

    for lot in lots:
        raw_lots.append(market_pb2.Lot(item_type=lot.full_type,
                                       item_id=lot.item_id.hex,
                                       owner_id=lot.owner_id,
                                       price=lot.price))

    tt_api.sync_request(url=conf.payments_settings.TT_PLACE_SELL_LOT_URL,
                        data=market_pb2.PlaceSellLotRequest(lots=raw_lots),
                        AnswerType=market_pb2.PlaceSellLotResponse)

def info(owner_id=None):
    request = market_pb2.InfoRequest()

    if owner_id is not None:
        request.owner_id = owner_id

    answer = tt_api.sync_request(url=conf.payments_settings.TT_INFO_URL,
                                 data=request,
                                 AnswerType=market_pb2.InfoResponse)

    data = []

    for info in answer.info:
        data.append(objects.ItemTypeSummary(full_type=info.item_type,
                                            sell_number=info.sell_number,
                                            min_sell_price=info.min_sell_price,
                                            max_sell_price=info.max_sell_price,
                                            owner_sell_number=info.owner_sell_number))

    return data


def item_type_prices(item_type, owner_id):
    answer = tt_api.sync_request(url=conf.payments_settings.TT_ITEM_TYPE_PRICES_URL,
                                 data=market_pb2.ItemTypePricesRequest(item_type=item_type,
                                                                       owner_id=owner_id),
                                 AnswerType=market_pb2.ItemTypePricesResponse)

    return dict(answer.prices), dict(answer.owner_prices)


def close_lot(item_type, price, buyer_id):
    answer = tt_api.sync_request(url=conf.payments_settings.TT_CLOSE_SELL_LOT_URL,
                                 data=market_pb2.CloseSellLotRequest(item_type=item_type,
                                                                     price=price,
                                                                     number=1,
                                                                     buyer_id=buyer_id),
                                 AnswerType=market_pb2.CloseSellLotResponse)

    return [objects.Lot(owner_id=lot.owner_id,
                        full_type=lot.item_type,
                        item_id=uuid.UUID(lot.item_id),
                        price=lot.price) for lot in answer.lots]


def cancel_lot(item_type, price, owner_id):
    answer = tt_api.sync_request(url=conf.payments_settings.TT_CANCEL_SELL_LOT_URL,
                                 data=market_pb2.CancelSellLotRequest(item_type=item_type,
                                                                      price=price,
                                                                      number=1,
                                                                      owner_id=owner_id),
                                 AnswerType=market_pb2.CancelSellLotResponse)

    return [objects.Lot(owner_id=lot.owner_id,
                        full_type=lot.item_type,
                        item_id=uuid.UUID(lot.item_id),
                        price=lot.price) for lot in answer.lots]


def list_sell_lots(owner_id):
    answer = tt_api.sync_request(url=conf.payments_settings.TT_LIST_SELL_LOTS_URL,
                                 data=market_pb2.ListSellLotsRequest(owner_id=owner_id),
                                 AnswerType=market_pb2.ListSellLotsResponse)
    return [objects.Lot(owner_id=owner_id,
                        full_type=lot.item_type,
                        item_id=uuid.UUID(lot.item_id),
                        price=lot.price,
                        created_at=datetime.datetime.fromtimestamp(lot.created_at)) for lot in answer.lots]


def history(page, records_on_page):
    answer = tt_api.sync_request(url=conf.payments_settings.TT_HISTORY_URL,
                                 data=market_pb2.HistoryRequest(page=page, records_on_page=records_on_page),
                                 AnswerType=market_pb2.HistoryResponse)
    records = [objects.LogRecord(item_type=record.item_type,
                                 created_at=datetime.datetime.fromtimestamp(record.created_at),
                                 price=record.price) for record in answer.records]
    return answer.page, answer.total_records, records


def statistics(time_from, time_till):
    answer = tt_api.sync_request(url=conf.payments_settings.TT_STATISTICS_URL,
                                 data=market_pb2.StatisticsRequest(time_from=time.mktime(time_from.timetuple())+time_from.microsecond/10**6,
                                                                   time_till=time.mktime(time_till.timetuple())+time_till.microsecond/10**6),
                                 AnswerType=market_pb2.StatisticsResponse)
    return {'sell_lots_placed': answer.sell_lots_placed,
            'sell_lots_closed': answer.sell_lots_closed,
            'turnover': answer.turnover}


def debug_clear_service():
    if project_settings.TESTS_RUNNING:
        tt_api.sync_request(url=conf.payments_settings.TT_DEBUG_CLEAR_SERVICE_URL,
                            data=market_pb2.DebugClearServiceRequest(),
                            AnswerType=market_pb2.DebugClearServiceResponse)
