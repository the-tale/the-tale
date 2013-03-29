# coding: utf-8

from dext.utils.app_settings import app_settings

news_settings = app_settings('NEWS',
                             FORUM_CATEGORY_SLUG='news',
                             NEWS_ON_PAGE=10,
                             FEED_ITEMS_NUMBER=10,
                             FEED_ITEMS_DELAY=2*60*60)
