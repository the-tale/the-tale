# coding: utf-8
from django.core.urlresolvers import reverse_lazy

from dext.utils.app_settings import app_settings

news_settings = app_settings('NEWS',
                             FORUM_CATEGORY_SLUG='news',
                             RSS_LINK=reverse_lazy('news:feed'),
                             NEWS_ON_PAGE=10,
                             FEED_ITEMS_NUMBER=10,
                             FEED_ITEMS_DELAT=2*60*60)
