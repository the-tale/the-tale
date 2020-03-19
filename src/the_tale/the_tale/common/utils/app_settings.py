
import smart_imports
smart_imports.all()


class AppSettings(object):
    pass


def app_settings(prefix, **kwargs):
    settings = AppSettings()

    for key, default_value in kwargs.items():
        project_key = '%s_%s' % (prefix, key)
        if hasattr(django_settings, project_key):
            setattr(settings, key, getattr(django_settings, project_key))
        else:
            setattr(settings, key, default_value)

    return settings
