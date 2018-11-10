
import datetime

from tt_web import s11n
from tt_web import handlers

from tt_web.common import pagination

from tt_protocol.protocol import events_log_pb2

from . import protobuf
from . import operations


@handlers.api(events_log_pb2.AddEventRequest)
async def add_event(message, **kwargs):
    await operations.add_event(tags=frozenset(message.tags),
                               data=s11n.from_json(message.data),
                               turn=message.turn,
                               time=datetime.datetime.fromtimestamp(message.time))
    return events_log_pb2.AddEventResponse()


@handlers.api(events_log_pb2.GetEventsRequest)
async def get_events(message, **kwargs):
    tags = frozenset(message.tags)

    records_number = await operations.events_number(tags=tags)

    page = pagination.normalize_page(page=message.page,
                                     records_number=records_number,
                                     records_on_page=message.records_on_page)

    if not tags:
        events = await operations.get_all_events(page=page,
                                                 records_on_page=message.records_on_page)
    else:
        events = await operations.get_events_by_tags(tags=tags,
                                                     page=page,
                                                     records_on_page=message.records_on_page)

    return events_log_pb2.GetEventsResponse(events=[protobuf.from_event(event) for event in events],
                                            page=page,
                                            total_records=records_number)


@handlers.api(events_log_pb2.GetLastEventsRequest)
async def get_last_events(message, **kwargs):
    tags = frozenset(message.tags)

    records_number = await operations.events_number(tags=tags)

    if not tags:
        events = await operations.get_all_last_events(number=message.number)
    else:
        events = await operations.get_last_events_by_tags(tags=tags,
                                                          number=message.number)

    return events_log_pb2.GetLastEventsResponse(events=[protobuf.from_event(event) for event in events],
                                                total_records=records_number)


@handlers.api(events_log_pb2.DebugClearServiceRequest)
async def debug_clear_service(message, **kwargs):
    await operations.clean_database()
    return events_log_pb2.DebugClearServiceResponse()
