# coding: utf-8

import jinja2

from dext.jinja2.decorators import jinjaglobal

from the_tale.accounts import logic
from the_tale.accounts.conf import accounts_settings


@jinjaglobal
def login_page_url(next_url='/'):
    return jinja2.Markup(logic.login_page_url(next_url))

@jinjaglobal
def login_url(next_url='/'):
    return jinja2.Markup(logic.login_url(next_url))

@jinjaglobal
def logout_url():
    return jinja2.Markup(logic.logout_url())

@jinjaglobal
def forum_complaint_theme():
    return accounts_settings.FORUM_COMPLAINT_THEME
