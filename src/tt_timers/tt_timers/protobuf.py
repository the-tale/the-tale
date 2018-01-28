
import time

from tt_protocol.protocol import timers_pb2


def from_timer(timer):
    return timers_pb2.Timer(id=timer.id,
                            owner_id=timer.owner_id,
                            entity_id=timer.entity_id,
                            type=timer.type,
                            speed=timer.speed,
                            border=timer.border,
                            resources=timer.resources,
                            resources_at=time.mktime(timer.resources_at.timetuple()) + timer.resources_at.microsecond / 1000000,
                            finish_at=time.mktime(timer.finish_at.timetuple()) + timer.finish_at.microsecond / 1000000)
