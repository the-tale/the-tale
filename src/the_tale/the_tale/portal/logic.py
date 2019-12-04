
import smart_imports

smart_imports.all()


def cdn_paths():

    if django_settings.CDNS_ENABLED and conf.settings.SETTINGS_CDN_INFO_KEY in global_settings:
        return s11n.from_json(global_settings[conf.settings.SETTINGS_CDN_INFO_KEY])

    return utils_cdn.get_local_paths(django_settings.CDNS)
