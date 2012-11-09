# coding: utf-8

from dext.utils.app_settings import app_settings

pvp_settings = app_settings('PVP',
                            BALANCER_SLEEP_TIME=5,

                            BALANCING_TIMEOUT=30*60,
                            BALANCING_MAX_LEVEL_DELTA=5
    )
