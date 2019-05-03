
from tt_web import exceptions


class MatchmakerError(exceptions.BaseError):
    pass


class BattleParticipantsIntersection(MatchmakerError):
    MESSAGE = 'Participant {participant} already participate in another battle'


class DuplicateBattleParticipants(MatchmakerError):
    MESSAGE = 'Duplicate battle participants: {participants}'


class NoBattleRequestFound(MatchmakerError):
    MESSAGE = 'No battle request {battle_request} found'
