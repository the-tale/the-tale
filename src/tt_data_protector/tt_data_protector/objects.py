
import uuid
import datetime
import dataclasses

from . import relations


@dataclasses.dataclass(frozen=True)
class Report:
    __slots__ = ('id', 'state', 'data', 'completed_at', 'expire_at')

    id: uuid.UUID
    state: relations.REPORT_STATE
    data: dict
    completed_at: datetime.datetime
    expire_at: datetime.datetime

    def is_expired(self):

        if self.state != relations.REPORT_STATE.READY:
            return False

        if self.expire_at is None:
            return False

        return self.expire_at < datetime.datetime.now(datetime.timezone.utc)


@dataclasses.dataclass(frozen=True)
class SubReport:
    __slots__ = ('id', 'report_id', 'source', 'state', 'data')

    id: int
    report_id: uuid.UUID
    state: relations.SUBREPORT_STATE
    source: str
    data: dict

    def replace(self, state=None, data=None):
        arguments = {}

        if state is not None:
            arguments['state'] = state

        if data is not None:
            arguments['data'] = data

        return dataclasses.replace(self, **arguments)


@dataclasses.dataclass(frozen=True)
class DeletionRequest:
    __slots__ = ('id', 'source', 'data')

    id: int
    source: str
    data: dict

    def replace(self, data=None):
        arguments = {}

        if data is not None:
            arguments['data'] = data

        return dataclasses.replace(self, **arguments)
