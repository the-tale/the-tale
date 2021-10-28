
import smart_imports

smart_imports.all()


settings = utils_app_settings.app_settings('CLANS',
                                           CLANS_ON_PAGE=25,
                                           TT_CHRONICLE_ENTRY_POINT='http://tt_clans_chronicle:80/',
                                           TT_CLANS_PROPERTIES_ENTRY_POINT='http://tt_clans_properties:80/',
                                           TT_CLANS_POINTS_ENTRY_POINT='http://tt_clans_currencies:80/',
                                           CLANS_POINTS_TRANSACTION_LIFETIME=24 * 60 * 60,
                                           CHRONICLE_RECORDS_ON_CLAN_PAGE=25,
                                           FORUM_CATEGORY_SLUG='clans',
                                           RECRUITE_FREEZE_PERIOD=7)
