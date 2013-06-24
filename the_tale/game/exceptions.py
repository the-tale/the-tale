# coding: utf-8

from common.utils.exceptions import TheTaleError

class GameException(TheTaleError):
    MSG = u'game error'

class HeroAlreadyRegisteredError(GameException):
    MSG = u'Hero with id "%(hero_id)d" has already registerd in storage, probably on initialization step'

class RemoveActionFromMiddleError(GameException):
    MSG = u'try to remove action (%(action)r) from the middle of actions list, last action: (%(last_action)r). Actions list: %(actions_list)r'

class SupervisorTaskMemberMissedError(GameException):
    MSG = u'try process supervisor task %(task_id)d when not all members captured; members: %(members)r, captured members: %(captured_members)r'
