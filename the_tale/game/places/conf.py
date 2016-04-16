# coding: utf-8

from dext.common.utils.app_settings import app_settings

settings = app_settings('PLACES',
                        MAX_DESCRIPTION_LENGTH=1000,

                        CHRONICLE_RECORDS_NUMBER=10,

                        API_LIST_VERSION='1.1',
                        API_SHOW_VERSION='2.0')
