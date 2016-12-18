# coding: utf-8

from dext.common.utils.app_settings import app_settings


utils_settings = app_settings('UTILS',
                              OPEN_EXCHANGE_RATES_API_ID='openexchangerates.org key',
                              OPEN_EXCHANGE_RATES_API_LATEST_URL='http://openexchangerates.org/api/latest.json'
                              )
