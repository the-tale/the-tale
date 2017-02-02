
from dext.common.utils import jinja2

from . import logic


@jinja2.jinjaglobal
def region_url(turn=None):
    return logic.region_url(turn=turn)
