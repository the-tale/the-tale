# coding: utf-8

from dext.jinja2.decorators import jinjafilter

from the_tale.common.utils import logic


@jinjafilter
def verbose_timedelta(value):
    return logic.verbose_timedelta(value)


@jinjafilter
def absolutize_urls(value):
    return logic.absolutize_urls(value)
