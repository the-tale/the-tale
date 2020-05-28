
import smart_imports

smart_imports.all()


@utils_jinja2.jinjaglobal
def login_page_url(next_url='/'):
    return utils_jinja2.Markup(logic.login_page_url(next_url))


@utils_jinja2.jinjaglobal
def login_url(next_url='/'):
    return utils_jinja2.Markup(logic.login_url(next_url))


@utils_jinja2.jinjaglobal
def logout_url():
    return utils_jinja2.Markup(logic.logout_url())


@utils_jinja2.jinjaglobal
def register_url():
    return utils_jinja2.Markup(logic.register_url())


@utils_jinja2.jinjaglobal
def forum_complaint_theme():
    return conf.settings.FORUM_COMPLAINT_THEME


@utils_jinja2.jinjafilter
def data_protection_verbose(value):
    return data_protection.verbose(value)
