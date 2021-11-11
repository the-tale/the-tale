

import smart_imports

smart_imports.all()


@utils_jinja2.jinjafilter
def verbose_timedelta(value):
    return logic.verbose_timedelta(value)


@utils_jinja2.jinjafilter
def verbose_datetime(value):
    return value.strftime('%d.%m.%Y %H:%M')


@utils_jinja2.jinjaglobal
def verbose_to_datetime(to_time=None):

    now = datetime.datetime.now()

    if to_time is None:
        to_time = datetime.datetime.combine(now.date() + datetime.timedelta(days=1),
                                            datetime.time())

    return logic.verbose_timedelta(to_time - now)


@utils_jinja2.jinjafilter
def absolutize_urls(value):
    return logic.absolutize_urls(value)


@utils_jinja2.jinjafilter
def json(value):
    return utils_jinja2.Markup(s11n.to_json(value))


@utils_jinja2.jinjaglobal
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


@utils_jinja2.jinjafilter
def pprint_int(value):
    return ('{:,d}'.format(int(value)).replace(',', ' '))


@utils_jinja2.jinjaglobal
def jmap(func, *iterables):
    return list(map(func, *iterables))


@utils_jinja2.jinjaglobal
@utils_jinja2.contextfunction
def get_context(context):
    return context


@utils_jinja2.jinjafilter
def endl2br(value):
    return utils_jinja2.Markup(value.replace('\n\r', '</br>').replace('\n', r'</br>'))


@utils_jinja2.jinjafilter
def percents(value, points=0):
    return ('%' + ('.%d' % points) + 'f%%') % (round(value, 2 + points) * 100)


@utils_jinja2.jinjafilter
def timestamp(value):
    return time.mktime(value.timetuple())


@utils_jinja2.jinjaglobal
def now():
    return datetime.datetime.now()


@utils_jinja2.jinjafilter
def up_first(value):
    return logic.up_first(value)


@utils_jinja2.jinjaglobal
def is_sequence(variable):
    return not isinstance(variable, str) and isinstance(variable, collections.abc.Iterable)


@utils_jinja2.jinjaglobal
def url(*args, **kwargs):
    return utils_urls.url(*args, **kwargs)


@utils_jinja2.jinjaglobal
def full_url(*args, **kwargs):
    return utils_urls.full_url(*args, **kwargs)


@utils_jinja2.jinjaglobal
def absolute_url(*args, **kwargs):
    return utils_urls.absolute_url(*args, **kwargs)
