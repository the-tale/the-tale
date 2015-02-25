# coding: utf-8

from dext.common.utils.app_settings import app_settings

settings = app_settings('MARKET_SETTINGS',
                        LOTS_ON_PAGE=25,
                        LOT_LIVE_TIME=7, # in days
                        MINIMUM_PRICE=10,
                        HISTORY_TIME=30, # in days
                        COMMISSION=0.07
                        )
