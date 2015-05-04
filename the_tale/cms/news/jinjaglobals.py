# coding: utf-8
from dext.common.utils import jinja2

from the_tale.cms.news import logic


@jinja2.jinjaglobal
def get_last_news():
    try:
        return logic.load_last_news()
    except IndexError:
        return None
