# coding: utf-8
from dext.jinja2.decorators import jinjaglobal

from the_tale.cms.news import logic


@jinjaglobal
def get_last_news():
    try:
        return logic.load_last_news()
    except IndexError:
        return None
