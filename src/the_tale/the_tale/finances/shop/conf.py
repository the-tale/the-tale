# coding: utf-8

from django.conf import settings as project_settings

from dext.common.utils.app_settings import app_settings


payments_settings = app_settings('PAYMENTS',
                                 PREMIUM_CURRENCY_FOR_DOLLAR=100,
                                 ENABLE_REAL_PAYMENTS=False if not project_settings.TESTS_RUNNING else True,
                                 SETTINGS_ALLOWED_KEY='payments allowed',

                                 ALWAYS_ALLOWED_ACCOUNTS=[],

                                 RANDOM_PREMIUM_DAYS=30,

                                 MARKET_HISTORY_RECORDS_ON_PAGE=100,

                                 MARKET_COMISSION=0.1,
                                 MARKET_COMMISSION_OPERATION_UID='market-buy-commission',

                                 MARKET_STATISTICS_PERIOD=30*24*60*60,

                                 TT_PLACE_SELL_LOT_URL='http://localhost:10004/place-sell-lot',
                                 TT_CLOSE_SELL_LOT_URL='http://localhost:10004/close-sell-lot',
                                 TT_CANCEL_SELL_LOT_URL='http://localhost:10004/cancel-sell-lot',
                                 TT_INFO_URL='http://localhost:10004/info',
                                 TT_ITEM_TYPE_PRICES_URL='http://localhost:10004/item-type-prices',
                                 TT_HISTORY_URL='http://localhost:10004/history',
                                 TT_LIST_SELL_LOTS_URL='http://localhost:10004/list-sell-lots',
                                 TT_STATISTICS_URL='http://localhost:10004/statistics',
                                 TT_DEBUG_CLEAR_SERVICE_URL='http://localhost:10004/debug-clear-service',

                                 XSOLLA_ENABLED=False if not project_settings.TESTS_RUNNING else True,

                                 XSOLLA_RUB_FOR_PREMIUM_CURRENCY=0.013,

                                 # default values was gotten from documentation
                                 XSOLLA_BASE_LINK= 'https://secure.xsolla.com/paystation2/',
                                 XSOLLA_PID=6,
                                 XSOLLA_MARKETPLACE='paydesk',
                                 XSOLLA_THEME=115,
                                 XSOLLA_PROJECT=4521,
                                 XSOLLA_LOCAL='ru',
                                 XSOLLA_DESCRIPTION='покупка печенек',
                                 XSOLLA_ID_THEME='id_theme',

                                 XSOLLA_DIALOG_WIDTH=900,
                                 XSOLLA_DIALOG_HEIGHT=800,

                                 REFERRAL_BONUS=0.1)
