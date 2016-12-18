# coding: utf-8

from dext.common.utils.app_settings import app_settings

settings = app_settings('NEWS',
                        FORUM_CATEGORY_UID='news',
                        NEWS_ON_PAGE=10,
                        FEED_ITEMS_NUMBER=10,
                        FEED_ITEMS_DELAY=2*60*60)
