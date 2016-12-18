# coding: utf-8
import datetime

from dext.common.utils import jinja2

from the_tale.portal.conf import portal_settings

@jinja2.jinjaglobal
def faq_url():
    return jinja2.Markup(portal_settings.FAQ_URL)

@jinja2.jinjaglobal
def players_projects_url():
    return jinja2.Markup(portal_settings.PLAYERS_PROJECTS_URL)

@jinja2.jinjaglobal
def get_edition_number():
    return (datetime.datetime.now() - portal_settings.FIRST_EDITION_DATE).days + 1
