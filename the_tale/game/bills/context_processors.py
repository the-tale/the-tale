# coding: utf-8

from game.bills.conf import bills_settings

def bills_context(request): # pylint: disable=W0613
    return {'bills_settings': bills_settings}
