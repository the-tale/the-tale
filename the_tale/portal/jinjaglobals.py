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



@jinja2.jinjaglobal
def standy_statistics_url():
    return 'http://standy.github.io/the-tale-stats/'

@jinja2.jinjaglobal
def standy_statistics_place_url(place_id):
    return 'http://standy.github.io/the-tale-stats/#!place/%d' % place_id

@jinja2.jinjaglobal
def standy_statistics_clan_url(clan_id):
    return 'http://standy.github.io/the-tale-stats/#!clan/%d' % clan_id

@jinja2.jinjaglobal
def standy_statistics_account_url(account_id):
    return 'http://standy.github.io/the-tale-stats/#!player/%d' % account_id
