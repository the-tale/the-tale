
from enum import Enum


class LOT_TYPE(Enum):
    BUY = 1
    SELL = 2


class OPERATION_TYPE(Enum):
    PLACE_SELL_LOT = 1
    CLOSE_SELL_LOT = 2
    CANCEL_SELL_LOT = 3
