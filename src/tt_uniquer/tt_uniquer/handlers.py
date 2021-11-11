
from tt_web import handlers

from tt_protocol.protocol import uniquer_pb2

from . import operations


@handlers.protobuf_api(uniquer_pb2.GetIdRequest)
async def get_id(message, **kwargs):
    unique_id = await operations.get_id(key=message.key)
    return uniquer_pb2.GetIdResponse(unique_id=unique_id)


@handlers.protobuf_api(uniquer_pb2.DebugClearServiceRequest)
async def debug_clear_service(message, **kwargs):
    await operations.clean_database()
    return uniquer_pb2.DebugClearServiceResponse()
