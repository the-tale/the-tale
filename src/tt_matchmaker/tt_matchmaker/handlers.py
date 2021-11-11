
from tt_web import handlers
from tt_web import exceptions as tt_exceptions

from tt_protocol.protocol import matchmaker_pb2

from . import protobuf
from . import operations
from . import exceptions


@handlers.protobuf_api(matchmaker_pb2.CreateBattleRequestRequest)
async def create_battle_request(message, config, **kwargs):
    battle_request_id = await operations.create_battle_request(matchmaker_type=message.matchmaker_type,
                                                               initiator_id=message.initiator_id)

    return matchmaker_pb2.CreateBattleRequestResponse(battle_request_id=battle_request_id)


@handlers.protobuf_api(matchmaker_pb2.CancelBattleRequestRequest)
async def cancel_battle_request(message, config, **kwargs):
    await operations.cancel_battle_request(message.battle_request_id)
    return matchmaker_pb2.CancelBattleRequestResponse()


@handlers.protobuf_api(matchmaker_pb2.AcceptBattleRequestRequest)
async def accept_battle_request(message, config, **kwargs):
    try:
        battle_id, participants_ids = await operations.accept_battle_request(battle_request_id=message.battle_request_id,
                                                                             acceptor_id=message.acceptor_id)
    except exceptions.NoBattleRequestFound as e:
        raise tt_exceptions.ApiError(code='matchmaker.accept_battle_request.no_battle_request_found', message=str(e))
    except exceptions.DuplicateBattleParticipants as e:
        raise tt_exceptions.ApiError(code='matchmaker.accept_battle_request.duplicate_participants', message=str(e))
    except exceptions.BattleParticipantsIntersection as e:
        raise tt_exceptions.ApiError(code='matchmaker.accept_battle_request.participants_intersection', message=str(e))

    return matchmaker_pb2.AcceptBattleRequestResponse(battle_id=battle_id,
                                                      participants_ids=list(participants_ids))


@handlers.protobuf_api(matchmaker_pb2.CreateBattleRequest)
async def create_battle(message, config, **kwargs):

    try:
        battle_id = await operations.create_battle(matchmaker_type=message.matchmaker_type,
                                                   participants_ids=list(message.participants_ids))
    except exceptions.DuplicateBattleParticipants as e:
        raise tt_exceptions.ApiError(code='matchmaker.create_battle.duplicate_participants', message=str(e))
    except exceptions.BattleParticipantsIntersection as e:
        raise tt_exceptions.ApiError(code='matchmaker.create_battle.participants_intersection', message=str(e))

    return matchmaker_pb2.CreateBattleResponse(battle_id=battle_id)


@handlers.protobuf_api(matchmaker_pb2.GetBattleRequestsRequest)
async def get_battle_requests(message, config, **kwargs):
    battle_requests = await operations.load_battle_requests(battle_requests_ids=message.battle_requests_ids)

    return matchmaker_pb2.GetBattleRequestsResponse(battle_requests=[protobuf.from_battle_request(request)
                                                                     for request in battle_requests])


@handlers.protobuf_api(matchmaker_pb2.GetInfoRequest)
async def get_info(message, config, **kwargs):
    battle_requests = await operations.list_battle_requests(matchmaker_types=message.matchmaker_types)
    battles_number = await operations.active_battles_number(matchmaker_types=message.matchmaker_types)

    return matchmaker_pb2.GetInfoResponse(active_battles=battles_number,
                                          battle_requests=[protobuf.from_battle_request(request)
                                                           for request in battle_requests])


@handlers.protobuf_api(matchmaker_pb2.FinishBattleRequest)
async def finish_battle(message, config, **kwargs):
    await operations.finish_battle(message.battle_id)
    return matchmaker_pb2.FinishBattleResponse()


@handlers.protobuf_api(matchmaker_pb2.GetBattlesByParticipantsRequest)
async def get_battles_by_participants(message, config, **kwargs):
    battles = await operations.load_battles_by_participants(message.participants_ids)
    return matchmaker_pb2.GetBattlesByParticipantsResponse(battles=[protobuf.from_battle(battle)
                                                                    for battle in battles])


@handlers.protobuf_api(matchmaker_pb2.DebugClearServiceRequest)
async def debug_clear_service(message, **kwargs):
    await operations.clean_database()
    return matchmaker_pb2.DebugClearServiceResponse()
