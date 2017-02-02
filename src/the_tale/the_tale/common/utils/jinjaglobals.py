# coding: utf-8

from dext.common.utils import jinja2

from . import logic
from . import bbcode


@jinja2.jinjafilter
def verbose_timedelta(value):
    return logic.verbose_timedelta(value)


@jinja2.jinjafilter
def absolutize_urls(value):
    return logic.absolutize_urls(value)


@jinja2.jinjafilter
def bb(value):
    return jinja2.Markup(bbcode.render(value))


@jinja2.jinjafilter
def bb_safe(value):
    return jinja2.Markup(bbcode.safe_render(value))
