
from tt_web import exceptions


class MarketError(exceptions.BaseError):
    pass


class SellLotForItemAlreadyCreated(MarketError):
    MESSAGE = 'Sell lot for item {item_id} already created'


class SellLotMaximumPriceExceeded(MarketError):
    MESSAGE = 'Sell lot maximum price exceeded, price: {price}'


class SellLotPriceBelowZero(MarketError):
    MESSAGE = 'Sell lot price below zero, price: {price}'
