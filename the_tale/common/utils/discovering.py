# coding: utf-8
import functools


def discover_classes(classes_list, base_class):
    return ( class_
             for class_ in classes_list
             if isinstance(class_, type) and issubclass(class_, base_class) and class_ != base_class)


def automatic_discover(container, module_name):

    @functools.wraps(automatic_discover)
    def decorator(function):

        @functools.wraps(function)
        def wrapper():
            container.clear()

            from django.conf import settings as project_settings
            from django.utils.importlib import import_module
            from django.utils.module_loading import module_has_submodule

            for app in project_settings.INSTALLED_APPS:
                mod = import_module(app)

                try:
                    function(container, import_module('%s.%s' % (app, module_name)))
                except StandardError:
                    if module_has_submodule(mod, module_name):
                        raise

        return wrapper

    return decorator
