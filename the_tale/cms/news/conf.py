# coding: utf-8
from django.core.urlresolvers import reverse_lazy

from dext.utils.app_settings import app_settings

news_settings = app_settings('NEWS',
                             FORUM_CATEGORY_SLUG='news',
                             RSS_LINK=reverse_lazy('news:feed'),
                             FEED_ITEMS_NUMBER=10)
