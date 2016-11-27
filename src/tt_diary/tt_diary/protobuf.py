
from tt_protocol.protocol import diary_pb2


from . import objects


def to_message(pb_message):
    return objects.Message(timestamp=pb_message.timestamp,
                           turn_number=pb_message.turn_number,
                           type=pb_message.type,
                           game_time=pb_message.game_time,
                           game_date=pb_message.game_date,
                           position=pb_message.position,
                           message=pb_message.message,
                           variables=dict(pb_message.variables))


def from_message(message):
    return diary_pb2.Message(timestamp=message.timestamp,
                             turn_number=message.turn_number,
                             type=message.type,
                             game_time=message.game_time,
                             game_date=message.game_date,
                             position=message.position,
                             message=message.message,
                             variables=message.variables)


def from_diary(diary):

    pb_diary = diary_pb2.Diary(version=diary.version)

    pb_diary.messages.extend([from_message(message) for message in diary.messages()])

    return pb_diary
