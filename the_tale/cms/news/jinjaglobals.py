# -*- coding: utf-8 -*-
from dext.jinja2.decorators import jinjaglobal

from cms.news.conf import news_settings

@jinjaglobal
def get_rss_link():
    return news_settings.RSS_LINK
