

import smart_imports

smart_imports.all()


@dext_jinja2.jinjafilter
def verbose_timedelta(value):
    return logic.verbose_timedelta(value)


@dext_jinja2.jinjafilter
def verbose_datetime(value):
    return value.strftime('%d.%m.%Y %H:%M')


@dext_jinja2.jinjafilter
def absolutize_urls(value):
    return logic.absolutize_urls(value)


@dext_jinja2.jinjafilter
def make_paragraphs(value):
    return dext_jinja2.Markup(value.strip().replace('\n', '<br/>'))


@dext_jinja2.jinjafilter
def bb(value):
    return dext_jinja2.Markup(bbcode.render(value))


@dext_jinja2.jinjafilter
def bb_safe(value):
    return dext_jinja2.Markup(bbcode.safe_render(value))


@dext_jinja2.jinjafilter
def json(value):
    return dext_jinja2.Markup(s11n.to_json(value))


@dext_jinja2.jinjaglobal
def value(module, variable):
    if not hasattr(value, '_values'):
        value._values = {}

    key = (module, variable)

    if key not in value._values:
        module = importlib.import_module(module)
        value._values[key] = getattr(module, variable)

    return value._values[key]
