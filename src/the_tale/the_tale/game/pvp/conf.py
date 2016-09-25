# coding: utf-8

from dext.common.utils.app_settings import app_settings

pvp_settings = app_settings('PVP',
                            BALANCER_SLEEP_TIME=5,

                            BALANCING_TIMEOUT=5*60,
                            BALANCING_MAX_LEVEL_DELTA=16,
                            BALANCING_MIN_LEVEL_DELTA=4,

                            BALANCING_WITHOUT_LEVELS=False # remove level limitation
    )
