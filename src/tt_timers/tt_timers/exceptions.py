
from tt_web import exceptions


class TimersError(exceptions.BaseError):
    pass


class TimerAlreadyExists(TimersError):
    MESSAGE = 'Timer for owner: {owner_id}, entity: {entity_id}, type: {type} already exists'


class TimerNotFound(TimersError):
    MESSAGE = 'Can not find timer for owner: {owner_id}, entity: {entity_id}, type: {type}'


class WrongTimerType(TimersError):
    MESSAGE = 'Wrong timer type "{type}" for tymer {timer_id}'
