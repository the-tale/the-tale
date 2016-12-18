# coding: utf-8
import hashlib

from dext.common.utils.urls import UrlBuilder

from dext.common.utils import jinja2

from the_tale.finances.shop import conf


@jinja2.jinjaglobal
def shop_settings():
    return conf.payments_settings

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
