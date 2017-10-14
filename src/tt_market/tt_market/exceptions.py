
from tt_web import exceptions


class MarketError(exceptions.BaseError):
    pass


class SellLotForItemAlreadyCreated(MarketError):
    MESSAGE = 'Sell lot for item {item_id} already created'
