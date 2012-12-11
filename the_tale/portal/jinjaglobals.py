# coding: utf-8

from dext.jinja2.decorators import jinjaglobal

from portal.conf import portal_settings

@jinjaglobal
def faq_url():
    return portal_settings.FAQ_URL
