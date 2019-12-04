
import smart_imports

smart_imports.all()


@utils_jinja2.jinjaglobal
def faq_url():
    return utils_jinja2.Markup(conf.settings.FAQ_URL)


@utils_jinja2.jinjaglobal
def players_projects_url():
    return utils_jinja2.Markup(conf.settings.PLAYERS_PROJECTS_URL)


@utils_jinja2.jinjaglobal
def get_edition_number():
    return (datetime.datetime.now() - conf.settings.FIRST_EDITION_DATE).days + 1
