

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
def value(module, variable=None):
    if not hasattr(value, '_values'):
        value._values = {}

    key = (module, variable)

    if key not in value._values:
        module = importlib.import_module(module)

        if variable is None:
            value._values[key] = module
        else:
            value._values[key] = getattr(module, variable)

    return value._values[key]


@dext_jinja2.jinjafilter
def pprint_int(value):
    return ('{:,d}'.format(int(value)).replace(',', ' '))


@dext_jinja2.jinjaglobal
def jmap(func, *iterables):
    return list(map(func, *iterables))


@dext_jinja2.jinjaglobal
@dext_jinja2.contextfunction
def get_context(context):
    return context


@dext_jinja2.jinjafilter
def endl2br(value):
    return dext_jinja2.Markup(value.replace('\n\r', '</br>').replace('\n', r'</br>'))


@dext_jinja2.jinjafilter
def percents(value, points=0):
    return ('%' + ('.%d' % points) + 'f%%') % (round(value, 2 + points) * 100)


@dext_jinja2.jinjafilter
def timestamp(value):
    return time.mktime(value.timetuple())


@dext_jinja2.jinjaglobal
def now():
    return datetime.datetime.now()


@dext_jinja2.jinjafilter
def up_first(value):
    if value:
        return value[0].upper() + value[1:]
    return value


@dext_jinja2.jinjaglobal
def is_sequence(variable):
    return not isinstance(variable, str) and isinstance(variable, collections.Iterable)


@dext_jinja2.jinjaglobal
def url(*args, **kwargs):
    return dext_urls.url(*args, **kwargs)


@dext_jinja2.jinjaglobal
def full_url(*args, **kwargs):
    return dext_urls.full_url(*args, **kwargs)


@dext_jinja2.jinjaglobal
def absolute_url(*args, **kwargs):
    return dext_urls.absolute_url(*args, **kwargs)
