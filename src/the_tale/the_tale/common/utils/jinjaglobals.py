
import importlib

from dext.common.utils import s11n
from dext.common.utils import jinja2

from . import logic
from . import bbcode


@jinja2.jinjafilter
def verbose_timedelta(value):
    return logic.verbose_timedelta(value)


@jinja2.jinjafilter
def verbose_datetime(value):
    return value.strftime('%d.%m.%Y %H:%M')


@jinja2.jinjafilter
def absolutize_urls(value):
    return logic.absolutize_urls(value)


@jinja2.jinjafilter
def make_paragraphs(value):
    return jinja2.Markup(value.strip().replace('\n', '<br/>'))


@jinja2.jinjafilter
def bb(value):
    return jinja2.Markup(bbcode.render(value))


@jinja2.jinjafilter
def bb_safe(value):
    return jinja2.Markup(bbcode.safe_render(value))


@jinja2.jinjafilter
def json(value):
    return jinja2.Markup(s11n.to_json(value))


@jinja2.jinjaglobal
def value(module, variable):
    if not hasattr(value, '_values'):
        value._values = {}

    key = (module, variable)

    if key not in value._values:
        module = importlib.import_module(module)
        value._values[key] = getattr(module, variable)

    return value._values[key]
