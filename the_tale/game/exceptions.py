# coding: utf-8

from common.utils.exceptions import TheTaleError


class GameError(TheTaleError):
    MSG = u'game error'

class HeroAlreadyRegisteredError(GameError):
    MSG = u'Hero with id "%(hero_id)d" has already registerd in storage, probably on initialization step'

class RemoveActionFromMiddleError(GameError):
    MSG = u'try to remove action (%(action)r) from the middle of actions list, last action: (%(last_action)r). Actions list: %(actions_list)r'

class SupervisorTaskMemberMissedError(GameError):
    MSG = u'try process supervisor task %(task_id)d when not all members captured; members: %(members)r, captured members: %(captured_members)r'


#########################
# highlevel
#########################

class HighlevelError(GameError):
    MSG = u'highlevel error'

class ChangePowerError(HighlevelError):
    MSG = u"we can change power for place or person, but not both (and persons automatically add power to it's place); place: %(place_id)s, person: %(person_id)s"

class WrongHighlevelTurnNumber(HighlevelError):
    MSG = u'desinchonization: workers turn number %(expected_turn_number)d not equal to command turn number %(new_turn_number)d'
