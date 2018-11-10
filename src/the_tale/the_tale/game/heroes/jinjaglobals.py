
import smart_imports

smart_imports.all()


@dext_jinja2.jinjaglobal
def heroes_conf():
    return conf.settings
