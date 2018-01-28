
import datetime

from django.conf import settings as project_settings

from tt_protocol.protocol import timers_pb2

from the_tale.common.utils import tt_api
from the_tale.common.utils import exceptions as common_exceptions

from tt_logic.cards import constants as logic_cards_constants

from . import conf
from . import objects
from . import relations
from . import exceptions


def create_cards_timer(account_id):
    try:
        tt_api.sync_request(url=conf.accounts_settings.TT_PLAYERS_TIMERS_CREATE_TIMER,
                            data=timers_pb2.CreateTimerRequest(owner_id=account_id,
                                                               entity_id=0,
                                                               type=relations.PLAYER_TIMERS_TYPES.CARDS_MINER.value,
                                                               speed=logic_cards_constants.NORMAL_PLAYER_SPEED,
                                                               border=logic_cards_constants.RECEIVE_TIME,
                                                               resources=0,
                                                               callback_data=''),
                            AnswerType=timers_pb2.CreateTimerResponse)
    except common_exceptions.TTAPIUnexpectedAPIStatus:
        raise exceptions.CanNotCreateCardsTimer()


def change_cards_timer_speed(account_id, speed):
    try:
        tt_api.sync_request(url=conf.accounts_settings.TT_PLAYERS_TIMERS_CHANGE_SPEED,
                            data=timers_pb2.ChangeSpeedRequest(owner_id=account_id,
                                                               entity_id=0,
                                                               type=relations.PLAYER_TIMERS_TYPES.CARDS_MINER.value,
                                                               speed=speed),
                            AnswerType=timers_pb2.ChangeSpeedResponse)
    except common_exceptions.TTAPIUnexpectedAPIStatus:
        raise exceptions.CanNotChangeCardsTimerSpeed()


def get_owner_timers(account_id):
    answer = tt_api.sync_request(url=conf.accounts_settings.TT_PLAYERS_TIMERS_GET_OWNER_TIMERS,
                                 data=timers_pb2.GetOwnerTimersRequest(owner_id=account_id),
                                 AnswerType=timers_pb2.GetOwnerTimersResponse)
    return [objects.Timer(id=timer.id,
                          owner_id=timer.owner_id,
                          entity_id=timer.entity_id,
                          type=relations.PLAYER_TIMERS_TYPES(timer.type),
                          speed=timer.speed,
                          border=timer.border,
                          resources=timer.resources,
                          resources_at=datetime.datetime.fromtimestamp(timer.resources_at),
                          finish_at=datetime.datetime.fromtimestamp(timer.finish_at)) for timer in answer.timers]


def debug_clear_service():
    if not project_settings.TESTS_RUNNING:
        return

    tt_api.sync_request(url=conf.accounts_settings.TT_PLAYERS_TIMERS_DEBUG_CLEAR_SERVICE_URL,
                        data=timers_pb2.DebugClearServiceRequest(),
                        AnswerType=timers_pb2.DebugClearServiceResponse)
