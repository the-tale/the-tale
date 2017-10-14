
from tt_protocol.protocol import personal_messages_pb2

from . import objects


def from_message(message):
    return personal_messages_pb2.Message(id=message.id,
                                         created_at=message.created_at.timestamp(),
                                         sender_id=message.sender,
                                         recipients_ids=message.recipients,
                                         body=message.body)
