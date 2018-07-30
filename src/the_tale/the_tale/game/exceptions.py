
import smart_imports

smart_imports.all()


class GameError(utils_exceptions.TheTaleError):
    MSG = 'game error'


class HeroAlreadyRegisteredError(GameError):
    MSG = 'Hero with id "%(hero_id)d" has already registerd in storage, probably on initialization step'


class RemoveActionFromMiddleError(GameError):
    MSG = 'try to remove action (%(action)r) from the middle of actions list, last action: (%(last_action)r). Actions list: %(actions_list)r'


class SupervisorTaskMemberMissedError(GameError):
    MSG = 'try process supervisor task %(task_id)d when not all members captured; members: %(members)r, captured members: %(captured_members)r'


class UnknownNextStepError(GameError):
    MSG = 'unknown next_step value %(next_step)s in ComplexChangeTask'


class DublicateAccountRegistration(GameError):
    MSG = 'try to double register one account: id=%(account_id)s, owner: %(owner)s'


#########################
# highlevel
#########################


class HighlevelError(GameError):
    MSG = 'highlevel error'


class WrongHighlevelTurnNumber(HighlevelError):
    MSG = 'desinchonization: workers turn number %(expected_turn_number)d not equal to command turn number %(new_turn_number)d'
