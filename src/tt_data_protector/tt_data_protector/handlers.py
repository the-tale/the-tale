
import uuid

from tt_web import handlers
from tt_web import exceptions as tt_exceptions

from tt_protocol.protocol import data_protector_pb2

from . import protobuf
from . import operations


@handlers.api(data_protector_pb2.RequestReportRequest)
async def request_report(message, config, **kwargs):

    if len(message.ids) == 0:
        raise tt_exceptions.ApiError(code='data_protector.request_report.no_ids_specified',
                                     message='no user identifies specified, no data to collect')

    for source_info in message.ids:
        if source_info.source not in config['custom']['sources']:
            raise tt_exceptions.ApiError(code='data_protector.request_report.wrong_source_id',
                                         message=f'unknowm source: {source_info.source}')

    report_id = await operations.create_report_base([(source_info.source, source_info.id) for source_info in message.ids])

    return data_protector_pb2.RequestReportResponse(report_id=report_id.hex)


@handlers.api(data_protector_pb2.GetReportRequest)
async def get_report(message, **kwargs):
    report = await operations.get_report(uuid.UUID(message.report_id))
    return data_protector_pb2.GetReportResponse(report=protobuf.from_report(report))


@handlers.api(data_protector_pb2.RequestDeletionRequest)
async def request_deletion(message, config, **kwargs):

    if len(message.ids) == 0:
        raise tt_exceptions.ApiError(code='data_protector.request_deletion.no_ids_specified',
                                     message='no user identifies specified, no data to collect')

    for source_info in message.ids:
        if source_info.source not in config['custom']['sources']:
            raise tt_exceptions.ApiError(code='data_protector.request_deletion.wrong_source_id',
                                         message=f'unknowm source: {source_info.source}')

    await operations.mark_for_deletion(core_id=message.core_id,
                                       ids=[(source_info.source, source_info.id) for source_info in message.ids])

    return data_protector_pb2.RequestDeletionResponse()


@handlers.api(data_protector_pb2.DebugClearServiceRequest)
async def debug_clear_service(message, **kwargs):
    await operations.clean_database()
    return data_protector_pb2.DebugClearServiceResponse()
