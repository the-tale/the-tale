
import smart_imports

smart_imports.all()


settings = utils_app_settings.app_settings('NEWS',
                                           FORUM_CATEGORY_UID='news',
                                           NEWS_ON_PAGE=10,
                                           FEED_ITEMS_NUMBER=10,
                                           FEED_ITEMS_DELAY=2 * 60 * 60)
