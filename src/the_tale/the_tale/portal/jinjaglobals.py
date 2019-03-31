
import smart_imports

smart_imports.all()


@dext_jinja2.jinjaglobal
def faq_url():
    return dext_jinja2.Markup(conf.settings.FAQ_URL)


@dext_jinja2.jinjaglobal
def players_projects_url():
    return dext_jinja2.Markup(conf.settings.PLAYERS_PROJECTS_URL)


@dext_jinja2.jinjaglobal
def get_edition_number():
    return (datetime.datetime.now() - conf.settings.FIRST_EDITION_DATE).days + 1


@dext_jinja2.jinjafilter
def olbanize(value):
    from the_tale import olbanizator

    if 'пейшунаалбанскам' in value:
        return value

    return olbanizator.olbanize(value)
