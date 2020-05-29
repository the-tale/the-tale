
from tt_web import s11n
from tt_web import handlers
from tt_web import exceptions as tt_exceptions

from tt_protocol.protocol import properties_pb2
from tt_protocol.protocol import data_protector_pb2

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


@handlers.api(data_protector_pb2.PluginReportRequest, raw=True)
async def data_protection_collect_data(message, config, **kwargs):

    if config['custom']['data_protector']['secret'] != message.secret:
        raise tt_exceptions.ApiError(code='properties.data_protection_collect_data.wrong_secret',
                                     message='wrong secret code')

    report = await operations.get_data_report(object_id=int(message.account_id))

    return data_protector_pb2.PluginReportResponse(result=data_protector_pb2.PluginReportResponse.ResultType.SUCCESS,
                                                   data=s11n.to_json(report))


@handlers.api(data_protector_pb2.PluginDeletionRequest, raw=True)
async def data_protection_delete_data(message, config, **kwargs):
    if config['custom']['data_protector']['secret'] != message.secret:
        raise tt_exceptions.ApiError(code='properties.data_protection_delete_data.wrong_secret',
                                     message='wrong secret code')

    await operations.clean_object_properties(object_id=int(message.account_id))

    return data_protector_pb2.PluginDeletionResponse(result=data_protector_pb2.PluginDeletionResponse.ResultType.SUCCESS)


@handlers.api(properties_pb2.DebugClearServiceRequest)
async def debug_clear_service(message, **kwargs):
    await operations.clean_database()
    return properties_pb2.DebugClearServiceResponse()
