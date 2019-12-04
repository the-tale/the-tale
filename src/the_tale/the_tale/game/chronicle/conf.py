
import smart_imports

smart_imports.all()


settings = utils_app_settings.app_settings('CHRONICLE',
                                           TT_GAME_CHRONICLE_ENTRY_POINT='http://localhost:10011/',
                                           RECORDS_ON_PAGE=25)
