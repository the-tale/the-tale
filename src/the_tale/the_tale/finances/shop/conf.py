
import smart_imports

smart_imports.all()


settings = dext_app_settings.app_settings('PAYMENTS',
                                          PREMIUM_CURRENCY_FOR_DOLLAR=100,
                                          ENABLE_REAL_PAYMENTS=False if not django_settings.TESTS_RUNNING else True,
                                          SETTINGS_ALLOWED_KEY='payments allowed',

                                          ALWAYS_ALLOWED_ACCOUNTS=[],

                                          RANDOM_PREMIUM_DAYS=30,

                                          MARKET_HISTORY_RECORDS_ON_PAGE=100,

                                          MARKET_COMISSION=0.1,
                                          MARKET_COMMISSION_OPERATION_UID='market-buy-commission',

                                          MARKET_STATISTICS_PERIOD=30 * 24 * 60 * 60,

                                          TT_MARKET_ENTRY_POINT='http://localhost:10004/',

                                          XSOLLA_ENABLED=False if not django_settings.TESTS_RUNNING else True,

                                          XSOLLA_RUB_FOR_PREMIUM_CURRENCY=0.013,

                                          # default values was gotten from documentation
                                          XSOLLA_BASE_LINK='https://secure.xsolla.com/paystation2/',
                                          XSOLLA_PID=6,
                                          XSOLLA_MARKETPLACE='paydesk',
                                          XSOLLA_THEME=115,
                                          XSOLLA_PROJECT=4521,
                                          XSOLLA_LOCAL='ru',
                                          XSOLLA_DESCRIPTION='покупка печенек',
                                          XSOLLA_ID_THEME='id_theme',
                                          XSOLLA_SUPPORT='https://www.xsolla.com/modules/support/',

                                          XSOLLA_DIALOG_WIDTH=900,
                                          XSOLLA_DIALOG_HEIGHT=800,

                                          REFERRAL_BONUS=0.1,

                                          MAX_PRICE=1000000)
