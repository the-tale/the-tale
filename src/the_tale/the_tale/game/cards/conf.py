
from dext.common.utils.app_settings import app_settings


settings = app_settings('CARDS',
                        GET_API_VERSION='2.0',
                        COMBINE_API_VERSION='2.0',
                        USE_API_VERSION='2.0',
                        GET_CARDS_API_VERSION='2.0',
                        MOVE_TO_STORAGE_API_VERSION='2.0',
                        MOVE_TO_HAND_API_VERSION='2.0',
                        RECEIVE_API_VERSION='1.0',
                        TT_STORAGE_APPLY_URL='http://localhost:10003/apply',
                        TT_STORAGE_GET_ITEMS_URL='http://localhost:10003/get-items',
                        TT_STORAGE_HAS_ITEMS_URL='http://localhost:10003/has-items',
                        TT_STORAGE_DEBUG_CLEAR_SERVICE_URL='http://localhost:10003/debug-clear-service')
