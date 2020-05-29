
import enum


class REPORT_STATE(enum.Enum):
    PROCESSING = 1
    READY = 2
    NOT_EXISTS = 3


class SUBREPORT_STATE(enum.Enum):
    PROCESSING = 1
    READY = 2
