
import smart_imports

smart_imports.all()


settings = utils_app_settings.app_settings('CARDS',
                                           GET_API_VERSION='2.0',
                                           COMBINE_API_VERSION='3.0',
                                           USE_API_VERSION='2.0',
                                           GET_CARDS_API_VERSION='2.0',
                                           MOVE_TO_STORAGE_API_VERSION='2.0',
                                           MOVE_TO_HAND_API_VERSION='2.0',
                                           RECEIVE_API_VERSION='1.0',
                                           CHANGE_RECEIVE_MODE_API_VERSION='1.0',
                                           TT_STORAGE_ENTRY_POINT='http://tt_storage:80/')
