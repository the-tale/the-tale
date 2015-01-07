# coding: utf-8

from dext.jinja2.decorators import jinjaglobal

from the_tale.market import conf


@jinjaglobal
def market_settings():
    return conf.settings
