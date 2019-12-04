
import smart_imports

smart_imports.all()


settings = utils_app_settings.app_settings('PLACES',
                                           MAX_DESCRIPTION_LENGTH=1000,

                                           CHRONICLE_RECORDS_NUMBER=10,

                                           START_PLACE_SAFETY_PERCENTAGE=0.33,

                                           API_LIST_VERSION='1.1',
                                           API_SHOW_VERSION='2.2',

                                           TT_PLACES_EFFECTS_ENTRY_POINT='http://localhost:10019/')
