
import smart_imports

smart_imports.all()


settings = utils_app_settings.app_settings('RATINGS',
                                           ACCOUNTS_ON_PAGE=50,
                                           SETTINGS_UPDATE_TIMESTEMP_KEY='ratings updated at timestamp')
