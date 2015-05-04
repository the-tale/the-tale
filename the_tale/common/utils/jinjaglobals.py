# coding: utf-8

from dext.common.utils import jinja2

from the_tale.common.utils import logic


@jinja2.jinjafilter
def verbose_timedelta(value):
    return logic.verbose_timedelta(value)


@jinja2.jinjafilter
def absolutize_urls(value):
    return logic.absolutize_urls(value)
