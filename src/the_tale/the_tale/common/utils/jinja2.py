
import smart_imports

smart_imports.all()

import jinja2  # импортируем модуль из глобального окружения


contextfunction = jinja2.contextfunction
Markup = jinja2.Markup


def jinjaglobal(f):
    f._is_jinjaglobal = True
    return f


def jinjafilter(f):
    f._is_jinjafilter = True
    return f


def get_jinjaglobals(module):

    filter_functions = {}
    global_functions = {}

    for func_name in dir(module):
        func = getattr(module, func_name)

        if getattr(func, '_is_jinjaglobal', False):
            global_functions[func_name] = func

        if getattr(func, '_is_jinjafilter', False):
            filter_functions[func_name] = func

    return global_functions, filter_functions


def discover(environment):

    for app in django_settings.INSTALLED_APPS:
        mod = importlib.import_module(app)

        if not django_module_loading.module_has_submodule(mod, 'jinjaglobals'):
            continue

        jinjaglobals_module = importlib.import_module('%s.jinjaglobals' % app)

        global_functions, filter_functions = get_jinjaglobals(jinjaglobals_module)

        environment.globals.update(global_functions)
        environment.filters.update(filter_functions)


def get_loader(directories):
    filesystem_loader = jinja2.FileSystemLoader(directories)

    apps_loader_params = {}

    # use last application_name part as unique name, since django expect it's uniqueness
    for application in django_apps.apps.get_app_configs():
        apps_loader_params[application.name.split('.')[-1]] = jinja2.PackageLoader(application.name)

    apps_loader = jinja2.PrefixLoader(apps_loader_params)

    return jinja2.ChoiceLoader([filesystem_loader, apps_loader])


class Engine(django_template_backends_base.BaseEngine):
    app_dirname = 'jinja2'

    def __init__(self, params):
        params = params.copy()

        options = params.pop('OPTIONS').copy()

        options['loader'] = get_loader(options.pop('directories'))

        self.context_processors = options.pop('context_processors')

        super(Engine, self).__init__(params)
        self.env = jinja2.Environment(**options)
        discover(self.env)

    def from_string(self, template_code):
        return Template(self.env.from_string(template_code), engine=self)

    def get_template(self, template_name):
        try:
            return Template(self.env.get_template(template_name), engine=self)
        except jinja2.TemplateNotFound as exc:
            django_six.reraise(django_template.TemplateDoesNotExist,
                               django_template.TemplateDoesNotExist(exc.args),
                               sys.exc_info()[2])
        except jinja2.django_template.TemplateSyntaxError as exc:
            django_six.reraise(django_template.TemplateSyntaxError,
                               django_template.TemplateSyntaxError(exc.args),
                               sys.exc_info()[2])

    @django_functional.cached_property
    def template_context_processors(self):
        from django.template.context import _builtin_context_processors
        from django.utils.module_loading import import_string

        context_processors = _builtin_context_processors
        context_processors += tuple(self.context_processors)
        return tuple(import_string(path) for path in context_processors)


class Template(object):
    __slots__ = ('template', 'engine')

    def __init__(self, template, engine=None):
        self.template = template
        self.engine = engine

    def render(self, context=None, request=None):
        real_context = {}

        real_context['settings'] = django_settings

        if request is not None:
            real_context['request'] = request
            real_context['csrf_input'] = django_template_backends_utils.csrf_input_lazy(request)
            real_context['csrf_token'] = django_template_backends_utils.csrf_token_lazy(request)

            if self.engine:
                for processor in self.engine.template_context_processors:
                    real_context.update(processor(request))

        if context:
            real_context.update(context)

        return self.template.render(real_context)


def render(template_name, context, request=None):
    template = django_template.loader.get_template(template_name)
    return template.render(context=context, request=request)
