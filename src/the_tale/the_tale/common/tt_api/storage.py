
import smart_imports

smart_imports.all()


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

    def cmd_debug_clear_service(self):
        if not django_settings.TESTS_RUNNING:
            return

        operations.sync_request(url=self.url('debug-clear-service'),
                                data=tt_protocol_storage_pb2.DebugClearServiceRequest(),
                                AnswerType=tt_protocol_storage_pb2.DebugClearServiceResponse)
