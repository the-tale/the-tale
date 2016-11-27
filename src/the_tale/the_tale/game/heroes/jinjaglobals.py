
from dext.common.utils import jinja2

from . import conf


@jinja2.jinjaglobal
def heroes_conf():
    return conf.heroes_settings
