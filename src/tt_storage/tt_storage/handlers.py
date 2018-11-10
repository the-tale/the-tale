
import uuid

from tt_web import handlers
from tt_web import exceptions as tt_exceptions

from tt_protocol.protocol import storage_pb2

from . import protobuf
from . import exceptions
from . import operations


@handlers.api(storage_pb2.ApplyRequest)
async def apply(message, **kwargs):
    try:
        await operations.apply(operations=[protobuf.to_operation(operation) for operation in message.operations])
    except exceptions.OperationsError as e:
        raise tt_exceptions.ApiError(code='storage.apply.operation_error', message=str(e))

    return storage_pb2.ApplyResponse()


@handlers.api(storage_pb2.GetItemsRequest)
async def get_items(message, **kwargs):
    items = await operations.load_items(owner_id=message.owner_id)

    return storage_pb2.GetItemsResponse(items=[protobuf.from_item(item) for item in items])


@handlers.api(storage_pb2.HasItemsRequest)
async def has_items(message, **kwargs):
    has = await operations.has_items(owner_id=message.owner_id, items_ids=[uuid.UUID(item_id) for item_id in message.items_ids])
    return storage_pb2.HasItemsResponse(has=has)


@handlers.api(storage_pb2.DebugClearServiceRequest)
async def debug_clear_service(message, **kwargs):
    await operations.clean_database()
    return storage_pb2.DebugClearServiceResponse()
