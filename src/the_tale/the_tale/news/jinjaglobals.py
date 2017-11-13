
from dext.common.utils import jinja2

from the_tale.news import logic


@jinja2.jinjaglobal
def get_last_news():
    try:
        return logic.load_last_news()
    except IndexError:
        return None
