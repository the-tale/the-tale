
import enum


class TRANSACTION_STATE(enum.Enum):
    OPENED = 1
    COMMITED = 2
    ROLLBACKED = 3
