
import smart_imports

smart_imports.all()


settings = utils_app_settings.app_settings('PAYMENTS',
                                           PREMIUM_CURRENCY_FOR_DOLLAR=100,
                                           # ENABLE_REAL_PAYMENTS=False if not django_settings.TESTS_RUNNING else True,
                                           ENABLE_REAL_PAYMENTS=False,
                                           SETTINGS_ALLOWED_KEY='payments allowed',

                                           ALWAYS_ALLOWED_ACCOUNTS=[],

                                           MARKET_HISTORY_RECORDS_ON_PAGE=100,

                                           MARKET_COMISSION=0.1,
                                           MARKET_COMMISSION_OPERATION_UID='market-buy-commission',

                                           MARKET_STATISTICS_PERIOD=30 * 24 * 60 * 60,

                                           TT_MARKET_ENTRY_POINT='http://tt-market:80/',
                                           TT_XSOLLA_ENTRY_POINT='http://tt-xsolla:80/',

                                           # XSOLLA_ENABLED=False if not django_settings.TESTS_RUNNING else True,
                                           XSOLLA_ENABLED=False,
                                           XSOLLA_PAY_STATION_VERSION=3,
                                           XSOLLA_SUPPORT='https://www.xsolla.com/modules/support/',

                                           # XSOLLA PAYSTATION 2 CONFIGS
                                           # default values was gotten from documentation
                                           XSOLLA_BASE_LINK='https://secure.xsolla.com/paystation2/',
                                           XSOLLA_PID=6,
                                           XSOLLA_MARKETPLACE='paydesk',
                                           XSOLLA_THEME=115,
                                           XSOLLA_PROJECT=4521,
                                           XSOLLA_LOCAL='ru',
                                           XSOLLA_DESCRIPTION='покупка печенек',
                                           XSOLLA_ID_THEME='id_theme',
                                           XSOLLA_DIALOG_WIDTH=900,
                                           XSOLLA_DIALOG_HEIGHT=800,

                                           # XSOLLA PAYSTATION 3 CONFIGS
                                           XSOLLA_EMBED_SCRIPT_VERSION='1.2.2',
                                           XSOLLA_SANDBOX=True,

                                           REFERRAL_BONUS=0.1,

                                           MAX_PRICE=1000000,)
