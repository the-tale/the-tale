# coding: utf-8
import hashlib
import datetime

from dext.common.utils.urls import UrlBuilder

from dext.common.utils import jinja2

from . import conf
from . import logic
from . import tt_api


@jinja2.jinjaglobal
def shop_settings():
    return conf.payments_settings


@jinja2.jinjaglobal
def create_sell_lot_url():
    return jinja2.Markup(logic.create_sell_lot_url())


@jinja2.jinjaglobal
def close_sell_lot_url():
    return jinja2.Markup(logic.close_sell_lot_url())


@jinja2.jinjaglobal
def cancel_sell_lot_url():
    return jinja2.Markup(logic.cancel_sell_lot_url())


@jinja2.jinjaglobal
def info_url():
    return jinja2.Markup(logic.info_url())


@jinja2.jinjaglobal
def item_type_prices_url():
    return jinja2.Markup(logic.item_type_prices_url())


@jinja2.jinjaglobal
def xsolla_paystaion_widget_link(account):
    # TODO: sign
    url_builder = UrlBuilder(base=conf.payments_settings.XSOLLA_BASE_LINK)

    sign_params = {'v1': account.email,
                   'email': account.email,
                   conf.payments_settings.XSOLLA_ID_THEME: conf.payments_settings.XSOLLA_THEME,
                   'project': conf.payments_settings.XSOLLA_PROJECT}

    sign_md5 = hashlib.md5(''.join(sorted('%s=%s' % (k, v) for k,v in sign_params.items())).encode('utf-8')).hexdigest()

    attributes = {'v1': account.email,
                  'email': account.email,
                  conf.payments_settings.XSOLLA_ID_THEME: conf.payments_settings.XSOLLA_THEME,
                  'project': conf.payments_settings.XSOLLA_PROJECT,
                  'local': conf.payments_settings.XSOLLA_LOCAL,
                  'description': conf.payments_settings.XSOLLA_DESCRIPTION,
                  'sign': sign_md5}

    if conf.payments_settings.XSOLLA_MARKETPLACE is not None:
        attributes['marketplace'] = conf.payments_settings.XSOLLA_MARKETPLACE

    if conf.payments_settings.XSOLLA_PID is not None:
        attributes['pid'] = conf.payments_settings.XSOLLA_PID

    link = url_builder(**attributes)

    return link


@jinja2.jinjaglobal
def market_statistics():
    statistics = tt_api.statistics(time_from=datetime.datetime.utcnow() - datetime.timedelta(seconds=conf.payments_settings.MARKET_STATISTICS_PERIOD),
                                   time_till=datetime.datetime.utcnow() + datetime.timedelta(days=1))
    return statistics
