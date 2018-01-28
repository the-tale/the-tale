
from tt_web import handlers
from tt_web import exceptions as tt_exceptions

from tt_protocol.protocol import timers_pb2

from . import protobuf
from . import operations
from . import exceptions


@handlers.api(timers_pb2.CreateTimerRequest)
async def create_timer(message, config, **kwargs):

    if str(message.type) not in config['custom']['types']:
        raise tt_exceptions.ApiError(code='timers.create_timer.unknown_type', message='unknown timer type {}'.format(message.type))

    try:
        timer = await operations.create_timer(owner_id=message.owner_id,
                                              entity_id=message.entity_id,
                                              type=message.type,
                                              speed=message.speed,
                                              border=message.border,
                                              callback_data=message.callback_data,
                                              resources=message.resources)
    except exceptions.TimerAlreadyExists as e:
        raise tt_exceptions.ApiError(code='timers.create_timer.duplicate_timer', message=str(e))

    return timers_pb2.CreateTimerResponse(timer=protobuf.from_timer(timer))


@handlers.api(timers_pb2.GetOwnerTimersRequest)
async def get_owner_timers(message, **kwargs):
    timers = await operations.get_owner_timers(owner_id=message.owner_id)
    return timers_pb2.GetOwnerTimersResponse(timers=[protobuf.from_timer(timer) for timer in timers])


@handlers.api(timers_pb2.ChangeSpeedRequest)
async def change_speed(message, config, **kwargs):

    if str(message.type) not in config['custom']['types']:
        raise tt_exceptions.ApiError(code='timers.change_speed.unknown_type', message='unknown timer type {}'.format(message.type))

    try:
        timer = await operations.change_speed(owner_id=message.owner_id,
                                              entity_id=message.entity_id,
                                              type=message.type,
                                              speed=message.speed)
    except exceptions.TimerNotFound as e:
        raise tt_exceptions.ApiError(code='timers.change_speed.timer_not_found', message=str(e))

    return timers_pb2.ChangeSpeedResponse(timer=protobuf.from_timer(timer))


@handlers.api(timers_pb2.DebugClearServiceRequest)
async def debug_clear_service(message, **kwargs):
    await operations.clean_database()
    return timers_pb2.DebugClearServiceResponse()
