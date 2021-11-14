
import smart_imports

smart_imports.all()


settings = utils_app_settings.app_settings('PVP',
                                           MAX_RATING_LEVEL_DELTA=4,

                                           REFRESH_INFO_TIMEOUT=60,

                                           CALL_TO_ARENA_API_VERSION='0.1',
                                           LEAVE_ARENA_API_VERSION='0.1',
                                           ACCEPT_ARENA_BATTLE_API_VERSION='0.1',
                                           CREATE_ARENA_BOT_BATTLE_API_VERSION='0.1',
                                           INFO_API_VERSION='0.1',

                                           TT_MATCHMAKER_ENTRY_POINT='http://tt-matchmaker:80/')
