# coding: utf-8

# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError


class MarketError(TheTaleError):
    MSG = 'market error'

class DuplicateGoodTypeUIDError(MarketError):
    MSG = 'duplicate good type uid "%(uid)s" for good type %(good_type)s'
