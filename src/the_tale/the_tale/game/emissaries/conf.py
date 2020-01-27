
import smart_imports

smart_imports.all()


settings = utils_app_settings.app_settings('EMISSARIES',
                                           CLAN_CHRONICLE_RECORDS_ON_EMISSARY_PAGE=5,
                                           GAME_CHRONICLE_RECORDS_ON_EMISSARY_PAGE=5,
                                           EVENTS_CURRENCIES_TRANSACTION_LIFETIME=2 * 60 * 60,

                                           # делаем таймаут чуть меньше расчётного,
                                           # чтобы на последнем цикле игрок мог получить карту
                                           CARD_RECEIVING_BY_EMISSARY_TIMEOUT=24 * 60 * 60 - 30 * 60,

                                           TT_EVENTS_CURRENCIES_ENTRY_POINT='http://localhost:10020/',
                                           TT_EVENTS_UNIQUER_ENTRY_POINT='http://localhost:10021/')
