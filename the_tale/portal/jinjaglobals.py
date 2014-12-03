# coding: utf-8
import jinja2

import datetime

from dext.jinja2.decorators import jinjaglobal

from the_tale.portal.conf import portal_settings

@jinjaglobal
def faq_url():
    return jinja2.Markup(portal_settings.FAQ_URL)

@jinjaglobal
def players_projects_url():
    return jinja2.Markup(portal_settings.PLAYERS_PROJECTS_URL)

@jinjaglobal
def get_edition_number():
    return (datetime.datetime.now() - portal_settings.FIRST_EDITION_DATE).days + 1



@jinjaglobal
def standy_statistics_url():
    return 'http://standy.github.io/the-tale-stats/'

@jinjaglobal
def standy_statistics_place_url(place_id):
    return 'http://standy.github.io/the-tale-stats/#!place/%d' % place_id

@jinjaglobal
def standy_statistics_clan_url(clan_id):
    return 'http://standy.github.io/the-tale-stats/#!clan/%d' % clan_id

@jinjaglobal
def standy_statistics_account_url(account_id):
    return 'http://standy.github.io/the-tale-stats/#!player/%d' % account_id
