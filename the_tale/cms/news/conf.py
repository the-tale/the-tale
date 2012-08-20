# coding: utf-8

from dext.utils.app_settings import app_settings

news_settings = app_settings('NEWS',
                             FORUM_CATEGORY_SLUG='news',
                             RSS_LINK='http://feeds.feedburner.com/The-Tale',
                             FEED_ITEMS_NUMBER=10)
