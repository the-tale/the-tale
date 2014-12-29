# coding: utf-8

# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError


class MarketError(TheTaleError):
    MSG = u'market error'

class DuplicateGoodTypeUIDError(MarketError):
    MSG = u'duplicate good type uid "%(uid)s" for good type %(good_type)s'
