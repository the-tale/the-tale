# coding: utf-8

from game.bills.conf import bills_settings

def bills_context(request):
    return {'bills_settings': bills_settings}
