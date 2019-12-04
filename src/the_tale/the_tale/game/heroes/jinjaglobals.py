
import smart_imports

smart_imports.all()


@utils_jinja2.jinjaglobal
def heroes_conf():
    return conf.settings
