# coding: utf-8
import jinja2

import datetime

from dext.jinja2.decorators import jinjaglobal

from portal.conf import portal_settings

@jinjaglobal
def faq_url():
    return jinja2.Markup(portal_settings.FAQ_URL)

@jinjaglobal
def get_edition_number():
    return (datetime.datetime.now() - portal_settings.FIRST_EDITION_DATE).days + 1
