
import smart_imports

smart_imports.all()


@dext_jinja2.jinjaglobal
def login_page_url(next_url='/'):
    return dext_jinja2.Markup(logic.login_page_url(next_url))


@dext_jinja2.jinjaglobal
def login_url(next_url='/'):
    return dext_jinja2.Markup(logic.login_url(next_url))


@dext_jinja2.jinjaglobal
def logout_url():
    return dext_jinja2.Markup(logic.logout_url())


@dext_jinja2.jinjaglobal
def forum_complaint_theme():
    return conf.settings.FORUM_COMPLAINT_THEME
