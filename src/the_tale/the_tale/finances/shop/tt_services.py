
import smart_imports

smart_imports.all()


class MarketClient(tt_api_market.Client):

    def lot_to_protobuf(self, lot):
        return tt_protocol_market_pb2.Lot(item_type=lot.full_type,
                                          item_id=lot.item_id.hex,
                                          owner_id=lot.owner_id,
                                          price=lot.price)

    def protobuf_to_lot(self, pb_lot):
        return objects.Lot(owner_id=pb_lot.owner_id,
                           full_type=pb_lot.item_type,
                           item_id=uuid.UUID(pb_lot.item_id),
                           price=pb_lot.price)

    def protobuf_to_lot_info(self, pb_lot):
        return objects.Lot(owner_id=None,
                           full_type=pb_lot.item_type,
                           item_id=uuid.UUID(pb_lot.item_id),
                           price=pb_lot.price,
                           created_at=datetime.datetime.fromtimestamp(pb_lot.created_at))

    def protobuf_to_item_type_summary(self, pb_summary):
        return objects.ItemTypeSummary(full_type=pb_summary.item_type,
                                       sell_number=pb_summary.sell_number,
                                       min_sell_price=pb_summary.min_sell_price,
                                       max_sell_price=pb_summary.max_sell_price,
                                       owner_sell_number=pb_summary.owner_sell_number)

    def protobuf_to_log_record(self, pb_record):
        return objects.LogRecord(item_type=pb_record.item_type,
                                 created_at=datetime.datetime.fromtimestamp(pb_record.created_at),
                                 price=pb_record.price)


market = MarketClient(entry_point=conf.settings.TT_MARKET_ENTRY_POINT)
