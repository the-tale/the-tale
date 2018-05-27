
from tt_web import handlers

from tt_protocol.protocol import impacts_pb2

from . import protobuf
from . import operations


@handlers.api(impacts_pb2.AddImpactsRequest)
async def add_impacts(message, config, **kwargs):
    impacts = [protobuf.to_impact(impact) for impact in message.impacts]

    await operations.add_impacts(impacts=impacts)

    return impacts_pb2.AddImpactsResponse()


@handlers.api(impacts_pb2.GetImpactsHistoryRequest)
async def get_impacts_history(message, config, **kwargs):

    if message.filter == impacts_pb2.GetImpactsHistoryRequest.FilterType.Value('NONE'):
        impacts = await operations.last_impacts(limit=message.limit)

    elif message.filter == impacts_pb2.GetImpactsHistoryRequest.FilterType.Value('ONLY_ACTOR'):
        impacts = await operations.last_actor_impacts(actor=protobuf.to_object(message.actor), limit=message.limit)

    elif message.filter == impacts_pb2.GetImpactsHistoryRequest.FilterType.Value('ONLY_TARGET'):
        impacts = await operations.last_target_impacts(target=protobuf.to_object(message.target), limit=message.limit)

    elif message.filter == impacts_pb2.GetImpactsHistoryRequest.FilterType.Value('BOTH'):
        impacts = await operations.last_actor_target_impacts(actor=protobuf.to_object(message.actor),
                                                             target=protobuf.to_object(message.target),
                                                             limit=message.limit)

    return impacts_pb2.GetImpactsHistoryResponse(impacts=[protobuf.from_impact(impact) for impact in impacts])


@handlers.api(impacts_pb2.GetTargetsImpactsRequest)
async def get_targets_impacts(message, config, **kwargs):
    impacts = await operations.get_targets_impacts([protobuf.to_object(target) for target in message.targets])
    return impacts_pb2.GetTargetsImpactsResponse(impacts=[protobuf.from_target_impact(impact) for impact in impacts])


@handlers.api(impacts_pb2.GetImpactersRatingsRequest)
async def get_impacters_ratings(message, config, **kwargs):
    ratings = await operations.get_impacters_ratings(targets=[protobuf.to_object(target) for target in message.targets],
                                                     actor_types=message.actor_types,
                                                     limit=message.limit)

    return impacts_pb2.GetImpactersRatingsResponse(ratings=[protobuf.from_rating(target, rating)
                                                            for target, rating in ratings.items()])


@handlers.api(impacts_pb2.ScaleImpactsRequest)
async def scale_impacts(message, config, **kwargs):
    await operations.scale_impacts(target_types=message.target_types, scale=message.scale)
    return impacts_pb2.ScaleImpactsResponse()


@handlers.api(impacts_pb2.DebugClearServiceRequest)
async def debug_clear_service(message, **kwargs):
    await operations.clean_database()
    return impacts_pb2.DebugClearServiceResponse()
