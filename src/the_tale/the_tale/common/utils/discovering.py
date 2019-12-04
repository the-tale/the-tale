
import smart_imports
smart_imports.all()


def is_module_exists(module_path):
    try:
        return importlib.import_module(module_path)
    except Exception:
        return False


def discover_classes(classes_list, base_class):
    return ( class_
             for class_ in classes_list
             if isinstance(class_, type) and issubclass(class_, base_class) and class_ != base_class)


def module_variables(module):
    for name in dir(module):
        yield getattr(module, name)


def discover_classes_in_module(module, base_class):
    return discover_classes(module_variables(module), base_class)


def automatic_discover(container, module_name):

    @functools.wraps(automatic_discover)
    def decorator(function):

        @functools.wraps(function)
        def wrapper(if_empty=False):
            if container and if_empty:
                return

            container.clear()

            for application in django_apps.apps.get_app_configs():
                mod = importlib.import_module(application.name)

                try:
                    function(container, importlib.import_module('%s.%s' % (application.name, module_name)))
                except Exception:
                    if django_module_loading.module_has_submodule(mod, module_name):
                        raise

        return wrapper

    return decorator


def get_function(function_path):
    module_path, function_name = function_path.rsplit('.', 1)
    module = importlib.import_module(module_path)
    return getattr(module, function_name)


def discover_modules_in_directory(path, prefix, exclude=('__init__.py',)):

    for name in os.listdir(path):
        if not name.endswith('.py'):
            continue

        if name in exclude:
            continue

        yield importlib.import_module('%s.%s' % (prefix, name[:-3]))
