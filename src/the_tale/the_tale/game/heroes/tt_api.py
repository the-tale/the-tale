
from tt_protocol.protocol import diary_pb2

from the_tale.common.utils import tt_api

from . import conf


def push_message_to_diary(account_id, message, is_premium):
    diary_size = conf.heroes_settings.DIARY_LOG_LENGTH_PREMIUM if is_premium else conf.heroes_settings.DIARY_LOG_LENGTH

    game_time = message.game_time()

    diary_message = diary_pb2.Message(timestamp=message.timestamp,
                                      turn_number=message.turn_number,
                                      type=message.key.value if message.key else None,
                                      game_time=game_time.verbose_time,
                                      game_date=game_time.verbose_date,
                                      position=message.position,
                                      message=message.message,
                                      variables=message.get_variables())

    tt_api.async_request(url=conf.heroes_settings.DIARY_PUSH_MESSAGE_URL,
                         data=diary_pb2.PushMessageRequest(account_id=account_id,
                                                           message=diary_message,
                                                           diary_size=diary_size))


def diary_version(account_id):
    answer = tt_api.sync_request(url=conf.heroes_settings.DIARY_VERSION_URL,
                                 data=diary_pb2.VersionRequest(account_id=account_id),
                                 AnswerType=diary_pb2.VersionResponse)

    return answer.version


def get_diary(account_id):
    answer = tt_api.sync_request(url=conf.heroes_settings.DIARY_URL,
                                 data=diary_pb2.DiaryRequest(account_id=account_id),
                                 AnswerType=diary_pb2.DiaryResponse)

    return answer.diary
