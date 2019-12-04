
import smart_imports

smart_imports.all()


@utils_jinja2.jinjaglobal
def shop_settings():
    return conf.settings


@utils_jinja2.jinjaglobal
def create_sell_lot_url():
    return utils_jinja2.Markup(logic.create_sell_lot_url())


@utils_jinja2.jinjaglobal
def close_sell_lot_url():
    return utils_jinja2.Markup(logic.close_sell_lot_url())


@utils_jinja2.jinjaglobal
def cancel_sell_lot_url():
    return utils_jinja2.Markup(logic.cancel_sell_lot_url())


@utils_jinja2.jinjaglobal
def info_url():
    return utils_jinja2.Markup(logic.info_url())


@utils_jinja2.jinjaglobal
def item_type_prices_url():
    return utils_jinja2.Markup(logic.item_type_prices_url())


@utils_jinja2.jinjaglobal
def xsolla_paystaion_widget_link(account):
    # TODO: sign
    url_builder = utils_urls.UrlBuilder(base=conf.settings.XSOLLA_BASE_LINK)

    sign_params = {'v1': account.email,
                   'email': account.email,
                   conf.settings.XSOLLA_ID_THEME: conf.settings.XSOLLA_THEME,
                   'project': conf.settings.XSOLLA_PROJECT}

    sign_md5 = hashlib.md5(''.join(sorted('%s=%s' % (k, v) for k, v in sign_params.items())).encode('utf-8')).hexdigest()

    attributes = {'v1': account.email,
                  'email': account.email,
                  conf.settings.XSOLLA_ID_THEME: conf.settings.XSOLLA_THEME,
                  'project': conf.settings.XSOLLA_PROJECT,
                  'local': conf.settings.XSOLLA_LOCAL,
                  'description': conf.settings.XSOLLA_DESCRIPTION,
                  'sign': sign_md5}

    if conf.settings.XSOLLA_MARKETPLACE is not None:
        attributes['marketplace'] = conf.settings.XSOLLA_MARKETPLACE

    if conf.settings.XSOLLA_PID is not None:
        attributes['pid'] = conf.settings.XSOLLA_PID

    link = url_builder(**attributes)

    return link


@utils_jinja2.jinjaglobal
def market_statistics():
    statistics = tt_services.market.cmd_statistics(time_from=datetime.datetime.utcnow() - datetime.timedelta(seconds=conf.settings.MARKET_STATISTICS_PERIOD),
                                                   time_till=datetime.datetime.utcnow() + datetime.timedelta(days=1))
    return statistics
