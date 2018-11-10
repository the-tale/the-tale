
import time

from tt_web import s11n

from tt_protocol.protocol import events_log_pb2


def from_event(event):
    return events_log_pb2.Event(id=event.id,
                                data=s11n.to_json(event.data),
                                tags=tuple(event.tags),
                                turn=event.created_at_turn,
                                time=time.mktime(event.created_at.timetuple())+event.created_at.microsecond / 1000000)
