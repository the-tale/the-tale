# coding: utf-8

import math

from accounts.payments.conf import payments_settings

def real_amount_to_game(amount):
    return int(math.ceil(amount * payments_settings.PREMIUM_CURRENCY_FOR_DOLLAR))
