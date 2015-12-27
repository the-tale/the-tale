# coding: utf-8

from dext.common.utils.app_settings import app_settings

settings = app_settings('PLACES',
                        MAX_SIZE=10,
                        MAX_FRONTIER_SIZE=7,
                        MAX_DESCRIPTION_LENGTH=1000,
                        BUILDING_POSITION_RADIUS=2,
                        NEW_PLACE_LIVETIME=2*7*24*60*60,
                        MIN_SAFETY=0.05,
                        MIN_TRANSPORT=0.1,
                        MIN_STABILITY=0,

                        CHRONICLE_RECORDS_NUMBER=10,

                        API_LIST_VERSION='1.0',
                        API_SHOW_VERSION='1.0')
