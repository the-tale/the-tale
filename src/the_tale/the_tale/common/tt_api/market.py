import smart_imports

smart_imports.all()


class Client(client.Client):

    def lot_to_protobuf(self, lot):
        raise NotImplementedError

    def protobuf_to_lot(self, pb_lot):
        raise NotImplementedError

    def protobuf_to_item_type_summary(self, pb_summary):
        raise NotImplementedError

    def protobuf_to_log_record(self, pb_record):
        raise NotImplementedError

    def cmd_place_sell_lots(self, lots):

        raw_lots = []

        for lot in lots:
            raw_lots.append(self.lot_to_protobuf(lot))

        operations.sync_request(url=self.url('place-sell-lot'),
                                data=tt_protocol_market_pb2.PlaceSellLotRequest(lots=raw_lots),
                                AnswerType=tt_protocol_market_pb2.PlaceSellLotResponse)

    def cmd_info(self, owner_id=None):
        request = tt_protocol_market_pb2.InfoRequest()

        if owner_id is not None:
            request.owner_id = owner_id

        answer = operations.sync_request(url=self.url('info'),
                                         data=request,
                                         AnswerType=tt_protocol_market_pb2.InfoResponse)

        data = []

        for info in answer.info:
            data.append(self.protobuf_to_item_type_summary(info))

        return data

    def cmd_item_type_prices(self, item_type, owner_id):
        answer = operations.sync_request(url=self.url('item-type-prices'),
                                         data=tt_protocol_market_pb2.ItemTypePricesRequest(item_type=item_type,
                                                                                           owner_id=owner_id),
                                         AnswerType=tt_protocol_market_pb2.ItemTypePricesResponse)

        return dict(answer.prices), dict(answer.owner_prices)

    def cmd_close_lot(self, item_type, price, buyer_id):
        answer = operations.sync_request(url=self.url('close-sell-lot'),
                                         data=tt_protocol_market_pb2.CloseSellLotRequest(item_type=item_type,
                                                                                         price=price,
                                                                                         number=1,
                                                                                         buyer_id=buyer_id),
                                         AnswerType=tt_protocol_market_pb2.CloseSellLotResponse)

        return [self.protobuf_to_lot(lot) for lot in answer.lots]

    def cmd_cancel_lot(self, item_type, price, owner_id):
        answer = operations.sync_request(url=self.url('cancel-sell-lot'),
                                         data=tt_protocol_market_pb2.CancelSellLotRequest(item_type=item_type,
                                                                                          price=price,
                                                                                          number=1,
                                                                                          owner_id=owner_id),
                                         AnswerType=tt_protocol_market_pb2.CancelSellLotResponse)

        return [self.protobuf_to_lot(lot) for lot in answer.lots]

    def cmd_list_sell_lots(self, owner_id):
        answer = operations.sync_request(url=self.url('list-sell-lots'),
                                         data=tt_protocol_market_pb2.ListSellLotsRequest(owner_id=owner_id),
                                         AnswerType=tt_protocol_market_pb2.ListSellLotsResponse)

        lots = []

        for pb_lot in answer.lots:
            lot = self.protobuf_to_lot_info(pb_lot)
            lot.owner_id = owner_id
            lots.append(lot)

        return lots

    def cmd_history(self, page, records_on_page):
        answer = operations.sync_request(url=self.url('history'),
                                         data=tt_protocol_market_pb2.HistoryRequest(page=page, records_on_page=records_on_page),
                                         AnswerType=tt_protocol_market_pb2.HistoryResponse)

        records = [self.protobuf_to_log_record(record) for record in answer.records]

        return answer.page, answer.total_records, records

    def cmd_statistics(self, time_from, time_till):
        answer = operations.sync_request(url=self.url('statistics'),
                                         data=tt_protocol_market_pb2.StatisticsRequest(time_from=time.mktime(time_from.timetuple()) + time_from.microsecond / 10**6,
                                                                                       time_till=time.mktime(time_till.timetuple()) + time_till.microsecond / 10**6),
                                         AnswerType=tt_protocol_market_pb2.StatisticsResponse)
        return {'sell_lots_placed': answer.sell_lots_placed,
                'sell_lots_closed': answer.sell_lots_closed,
                'turnover': answer.turnover}

    def cmd_debug_clear_service(self):
        if django_settings.TESTS_RUNNING:
            operations.sync_request(url=self.url('debug-clear-service'),
                                    data=tt_protocol_market_pb2.DebugClearServiceRequest(),
                                    AnswerType=tt_protocol_market_pb2.DebugClearServiceResponse)
