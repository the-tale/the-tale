
import time

from tt_protocol.protocol import matchmaker_pb2


def from_battle_request(battle_request):
    return matchmaker_pb2.BattleRequest(id=battle_request.id,
                                        initiator_id=battle_request.initiator_id,
                                        matchmaker_type=battle_request.matchmaker_type,
                                        created_at=time.mktime(battle_request.created_at.timetuple()),
                                        updated_at=time.mktime(battle_request.updated_at.timetuple()))


def from_battle(battle):
    return matchmaker_pb2.Battle(id=battle.id,
                                 matchmaker_type=battle.matchmaker_type,
                                 participants_ids=battle.participants_ids,
                                 created_at=time.mktime(battle.created_at.timetuple()))
