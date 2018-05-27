
import uuid
import time
import datetime

from tt_protocol.protocol import impacts_pb2

from . import objects


def to_object(pb_object):
    return objects.Object(type=pb_object.type, id=pb_object.id)


def from_object(object):
    return impacts_pb2.Object(type=object.type, id=object.id)


def to_impact(pb_impact, use_time=False):
    return objects.Impact(actor=to_object(pb_impact.actor),
                          target=to_object(pb_impact.target),
                          amount=pb_impact.amount,
                          turn=pb_impact.turn,
                          transaction=uuid.UUID(pb_impact.transaction),
                          time=datetime.datetime.fromtimestamp(pb_impact.time) if use_time else None)


def from_impact(impact):
    return impacts_pb2.Impact(actor=from_object(impact.actor),
                              target=from_object(impact.target),
                              amount=impact.amount,
                              transaction=impact.transaction.hex,
                              turn=impact.turn,
                              time=time.mktime(impact.time.timetuple())+impact.time.microsecond / 1000000)


def to_target_impact(pb_target_impact):
    return objects.TargetImpact(target=to_object(pb_target_impact.target),
                                amount=pb_target_impact.amount,
                                turn=pb_target_impact.turn,
                                time=datetime.datetime.fromtimestamp(pb_target_impact.time))


def from_target_impact(impact):
    return impacts_pb2.TargetImpact(target=from_object(impact.target),
                                    amount=impact.amount,
                                    turn=impact.turn,
                                    time=time.mktime(impact.time.timetuple())+impact.time.microsecond / 1000000)


def from_rating(target, rating):
    return impacts_pb2.Rating(target=from_object(target),
                              records=[impacts_pb2.RatingRecord(actor=from_object(record.actor), amount=record.amount)
                                       for record in rating])
