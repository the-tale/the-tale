
from tt_web import s11n
from tt_web import utils

from tt_protocol.protocol import data_protector_pb2


def from_report(report):
    return data_protector_pb2.Report(state=report.state.value,
                                     data=s11n.to_json(report.data['report']) if report.data is not None else '[]',
                                     completed_at=utils.postgres_time_to_timestamp(report.completed_at) if report.completed_at else None,
                                     expire_at=utils.postgres_time_to_timestamp(report.expire_at) if report.expire_at else None)
