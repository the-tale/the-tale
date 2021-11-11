
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


def fill_globals(environment):

    for app in django_settings.INSTALLED_APPS:
        mod = importlib.import_module(app)

        if not django_module_loading.module_has_submodule(mod, 'jinjaglobals'):
            continue

        jinjaglobals_module = importlib.import_module('%s.jinjaglobals' % app)

        global_functions, filter_functions = get_jinjaglobals(jinjaglobals_module)

        environment.globals.update(global_functions)
        environment.filters.update(filter_functions)


def create_loader(directories, package_path, packages=('the_tale',)):
    filesystem_loader = jinja2.FileSystemLoader(directories)

    apps_loader_params = {}

    # use last application_name part as unique name, since django expect it's uniqueness
    for application in django_apps.apps.get_app_configs():
        parts = application.name.split('.')

        if parts[0] not in packages:
            # load templates only for project applications
            continue

        templates_directory = os.path.join(django_settings.PROJECT_DIR,
                                           *parts[1:],
                                           package_path)

        apps_loader_params[parts[-1]] = jinja2.FileSystemLoader([templates_directory])

    apps_loader = jinja2.PrefixLoader(apps_loader_params)

    return jinja2.ChoiceLoader([filesystem_loader, apps_loader])


def create_environment(**options):
    environment = jinja2.Environment(**options)

    fill_globals(environment)

    return environment


class Backend(django_template_backends_jinja2.Jinja2):

    def __init__(self, params):
        if params['OPTIONS'].get('loader') is None:
            params['OPTIONS']['loader'] = create_loader(params['DIRS'], self.app_dirname)

        super().__init__(params)


def render(template_name, context, request=None):
    template = django_template.loader.get_template(template_name)
    return template.render(context=context, request=request)
