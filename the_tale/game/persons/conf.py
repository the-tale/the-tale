# coding: utf-8

from dext.common.utils.app_settings import app_settings


settings = app_settings('PERSONS',
                        API_SHOW_VERSION='1.0',
                        CHRONICLE_RECORDS_NUMBER=10,
                        SOCIAL_CONNECTIONS_MINIMUM=3,
                        SOCIAL_CONNECTIONS_AVERAGE_PATH_FRACTION=0.75,
                        SOCIAL_CONNECTIONS_MIN_DISTANCE_DECREASE=0.9)
