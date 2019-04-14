
from tt_web import handlers

from tt_protocol.protocol import properties_pb2

from . import protobuf
from . import operations


@handlers.api(properties_pb2.SetPropertiesRequest)
async def set_properties(message, config, **kwargs):
    await operations.set_properties([protobuf.to_property(property) for property in message.properties])
    return properties_pb2.SetPropertiesResponse()


@handlers.api(properties_pb2.GetPropertiesRequest)
async def get_properties(message, **kwargs):
    properties = await operations.get_properties({object_data.object_id: list(object_data.types)
                                                  for object_data in message.objects})
    return properties_pb2.GetPropertiesResponse(properties=[protobuf.from_property(property) for property in properties])


@handlers.api(properties_pb2.DebugClearServiceRequest)
async def debug_clear_service(message, **kwargs):
    await operations.clean_database()
    return properties_pb2.DebugClearServiceResponse()
