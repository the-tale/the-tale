# coding: utf-8

from dext.utils.app_settings import app_settings


ratings_settings = app_settings('RATINGS',
                                ACCOUNTS_ON_PAGE=50,
                                SETTINGS_UPDATE_TIMESTEMP_KEY='ratings updated at timestamp' )
