# coding: utf-8
from dext.jinja2.decorators import jinjaglobal

from cms.news.models import News

@jinjaglobal
def get_last_news():
    try:
        return News.objects.all().order_by('-created_at')[0]
    except IndexError:
        return None
