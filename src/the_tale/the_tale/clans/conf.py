
import smart_imports

smart_imports.all()


settings = dext_app_settings.app_settings('CLANS',
                                          CLANS_ON_PAGE=25,
                                          TT_CHRONICLE_ENTRY_POINT='http://localhost:10012/',
                                          TT_CLANS_PROPERTIES_ENTRY_POINT='http://localhost:10015/',
                                          CHRONICLE_RECORDS_ON_CLAN_PAGE=25,
                                          FORUM_CATEGORY_SLUG='clans',)
