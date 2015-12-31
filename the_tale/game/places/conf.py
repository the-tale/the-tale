# coding: utf-8

from dext.common.utils.app_settings import app_settings

settings = app_settings('PLACES',
                        MAX_DESCRIPTION_LENGTH=1000,
                        MIN_SAFETY=0.05,
                        MIN_TRANSPORT=0.1,
                        MIN_STABILITY=0,

                        CHRONICLE_RECORDS_NUMBER=10,

                        API_LIST_VERSION='1.0',
                        API_SHOW_VERSION='1.0')
