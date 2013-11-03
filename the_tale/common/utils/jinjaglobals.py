# coding: utf-8

from dext.jinja2.decorators import jinjafilter

from the_tale.common.utils.logic import verbose_timedelta as logic_verbose_timedelta


@jinjafilter
def verbose_timedelta(value):
    return logic_verbose_timedelta(value)
