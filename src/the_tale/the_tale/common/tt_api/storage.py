
import smart_imports

smart_imports.all()


class LogRecord:
    __slots__ = ('id', 'transaction', 'item_id', 'type', 'data', 'created_at')

    def __init__(self, id, transaction, item_id, type, data, created_at):
        self.id = id
        self.transaction = transaction
        self.item_id = item_id
        self.type = type
        self.data = data
        self.created_at = created_at

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                all(getattr(self, name) == getattr(other, name) for name in self.__slots__))

    def __ne__(self, other):
        return not self.__eq__(other)

    def serialize(self):
        return {'id': self.id,
                'transaction': self.transaction,
                'item_id': self.item_id,
                'type': self.type,
                'data': self.data,
                'created_at': self.created_at}


class Client(client.Client):
    __slots__ = ()

    def protobuf_to_item(self, pb_item):
        raise NotImplementedError

    def wrap_operation(self, operation, operation_type):
        operation.operation_type = operation_type

        if operation.__class__ == tt_protocol_storage_pb2.OperationCreate:
            return tt_protocol_storage_pb2.Operation(create=operation)

        if operation.__class__ == tt_protocol_storage_pb2.OperationDestroy:
            return tt_protocol_storage_pb2.Operation(destroy=operation)

        if operation.__class__ == tt_protocol_storage_pb2.OperationChangeOwner:
            return tt_protocol_storage_pb2.Operation(change_owner=operation)

        if operation.__class__ == tt_protocol_storage_pb2.OperationChangeStorage:
            return tt_protocol_storage_pb2.Operation(change_storage=operation)

        raise NotImplementedError

    def cmd_apply(self, applied_operations, operation_type):
        operations.sync_request(url=self.url('apply'),
                                data=tt_protocol_storage_pb2.ApplyRequest(operations=[self.wrap_operation(operation, operation_type)
                                                                                      for operation in applied_operations]),
                                AnswerType=tt_protocol_storage_pb2.ApplyResponse)

    def cmd_get_items(self, owner_id):
        answer = operations.sync_request(url=self.url('get-items'),
                                         data=tt_protocol_storage_pb2.GetItemsRequest(owner_id=owner_id),
                                         AnswerType=tt_protocol_storage_pb2.GetItemsResponse)

        items = {}

        for pb_item in answer.items:
            id, item = self.protobuf_to_item(pb_item)
            items[id] = item

        return items

    def cmd_has_items(self, owner_id, items_ids):
        answer = operations.sync_request(url=self.url('has-items'),
                                         data=tt_protocol_storage_pb2.HasItemsRequest(owner_id=owner_id, items_ids=items_ids),
                                         AnswerType=tt_protocol_storage_pb2.HasItemsResponse)
        return answer.has

    def cmd_get_item_logs(self, item_id):
        answer = operations.sync_request(url=self.url('get-item-logs'),
                                         data=tt_protocol_storage_pb2.GetItemLogsRequest(item_id=item_id),
                                         AnswerType=tt_protocol_storage_pb2.GetItemLogsResponse)
        return [LogRecord(id=record.id,
                          transaction=uuid.UUID(record.transaction),
                          item_id=uuid.UUID(record.item_id),
                          type=record.type,
                          data=s11n.from_json(record.data),
                          created_at=datetime.datetime.fromtimestamp(record.created_at))
                for record in answer.logs]

    def cmd_debug_clear_service(self):
        if not django_settings.TESTS_RUNNING:
            return

        operations.sync_request(url=self.url('debug-clear-service'),
                                data=tt_protocol_storage_pb2.DebugClearServiceRequest(),
                                AnswerType=tt_protocol_storage_pb2.DebugClearServiceResponse)
