
import uuid
import time

from tt_protocol.protocol import market_pb2

from . import objects
from . import relations


def to_sell_lot(pb_lot):
    return objects.Lot(type=relations.LOT_TYPE.SELL,
                       item_type=pb_lot.item_type,
                       item_id=uuid.UUID(pb_lot.item_id),
                       owner_id=pb_lot.owner_id,
                       price=pb_lot.price,
                       created_at=None)


def from_sell_lot(lot):
    return market_pb2.Lot(item_type=lot.item_type,
                          item_id=lot.item_id.hex,
                          owner_id=lot.owner_id,
                          price=lot.price)


def from_sell_lot_info(lot):
    return market_pb2.LotInfo(item_type=lot.item_type,
                              item_id=lot.item_id.hex,
                              price=lot.price,
                              created_at=time.mktime(lot.created_at.timetuple()))


def from_item_type_summary(summary):
    return market_pb2.ItemTypeSummary(item_type=summary.item_type,
                                      sell_number=summary.sell_number,
                                      min_sell_price=summary.min_sell_price,
                                      max_sell_price=summary.max_sell_price,
                                      owner_sell_number=summary.owner_sell_number)


def from_history_record(record):
    return market_pb2.LogRecord(item_type=record.item_type,
                                created_at=time.mktime(record.created_at.timetuple()),
                                price=record.price)
