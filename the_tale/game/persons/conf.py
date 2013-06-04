# coding: utf-8

from dext.utils.app_settings import app_settings

from game.balance import constants as c

POWER_HISTORY_WEEKS = 6

persons_settings = app_settings('PERSONS',
                                POWER_HISTORY_WEEKS=POWER_HISTORY_WEEKS,
                                POWER_HISTORY_LENGTH=POWER_HISTORY_WEEKS*7*24*c.TURNS_IN_HOUR,
                                POWER_STABILITY_PERCENT=0.05,
                                POWER_STABILITY_WEEKS=2 )
